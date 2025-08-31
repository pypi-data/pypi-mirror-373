import os
import logging
import datetime
import json
import ast
import jwt
import urllib #Needed for avoiding using requests, which modified the S3 presigned URL
from urllib.parse import urlparse, parse_qs
import csv
import pathlib
import socket, os


from .utils import convert_timestamps, send_post_request, send_get_request, decode_jwt_token, querystr_to_json, att2statement, send_delete_request
from .lineage_graph import create_lineage_graph 

from .constants import (
    SCRIBE_VULNERABILITIES_DATASET,
    SCRIBE_PRODUCTS_DATASET,
    SCRIBE_POLICY_DATASET,
    SCRIBE_TEAM_STAT_DATASET,
    SCRIBE_LINEAGE_DATASET,
    SCRIBE_RISK_DATASET,
    SCRIBE_FINDINGS_DATASET
)

# Event class for structured logging
class Event:
    def __init__(self, severity="INFO", messageid="2000", message="", timestamp=None, user=None, metadata=None):
        self.severity = severity
        self.messageid = messageid
        self.message = message
        self.timestamp = timestamp or datetime.datetime.now().isoformat()
        self.user = user
        self.metadata = metadata

    def to_dict(self):
        return {
            "severity": self.severity,
            "message": self.message,
            "messageid": self.messageid,
            "timestamp": self.timestamp,
            "user": self.user,
            "metadata": self.metadata,
        }

class ScribeClient:

    scribe_vulnerabilities_dataset = SCRIBE_VULNERABILITIES_DATASET
    scribe_products_dataset = SCRIBE_PRODUCTS_DATASET
    scribe_policy_dataset = SCRIBE_POLICY_DATASET
    scribe_team_stat_dataset = SCRIBE_TEAM_STAT_DATASET
    scribe_lineage_dataset=SCRIBE_LINEAGE_DATASET
    scribe_risk_dataset = SCRIBE_RISK_DATASET
    scribe_findings_dataset = SCRIBE_FINDINGS_DATASET

    def log_event(self, event: Event):
        """
        Log a structured event as an RFC5424 syslog message and upload to ScribeAPI /syslog endpoint.
        """

        # Validate input
        if not isinstance(event, Event):
            logging.error("log_event expects an Event instance")
            return

        # RFC5424: severity (0..7) and facility (0..23)
        severity_map = {
            "CRITICAL": 2,
            "ERROR": 3,
            "WARNING": 4,
            "INFO": 6,
            "DEBUG": 7,
        }
        facility = 0  # user-level (use 10 if you truly want authpriv)
        severity = severity_map.get(getattr(event, "severity", "INFO").upper(), 6)
        priority = (facility * 8) + severity

        # Header fields
        VERSION = 1  # RFC5424 version
        # Use RFC3339 timestamp with timezone (UTC)
        if getattr(event, "timestamp", None):
            # Ensure it's RFC3339; if it's naive, add 'Z'
            ts = str(event.timestamp)
            timestamp = ts if ("Z" in ts or "+" in ts) else (ts + "Z")
        # else:
            # timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

        hostname = socket.gethostname() or "-"
        app_name = "scribePythonClient"  # <=48 printable ASCII
        procid = str(os.getpid())          # "-" or up to 128 printable ASCII
        msgid = getattr(event, "messageid", None) or "pclient"  # <=32 printable ASCII

        # Structured data
        def sd_escape(val: str) -> str:
            # RFC5424: escape \, ", ]
            return str(val).replace("\\", "\\\\").replace('"', '\\"').replace("]", "\\]")

        # Validate metadata format: must be dict of dicts with str keys
        structured_data = "-"
        metadata = getattr(event, "metadata", None)
        if metadata:
            if not isinstance(metadata, dict) or not all(isinstance(v, dict) for v in metadata.values()):
                logging.error("Event.metadata must be a dict of dicts (key: dict)")
            else:
                sd_blocks = []
                for sd_id, params in metadata.items():
                    if not isinstance(params, dict):
                        continue
                    sd_params = " ".join(f'{k}="{sd_escape(v)}"' for k, v in params.items())
                    sd_blocks.append(f"[{sd_id} {sd_params}]")
                if sd_blocks:
                    structured_data = "".join(sd_blocks)
                else:
                    structured_data = "-"

        msg = getattr(event, "message", "") or ""

        # RFC5424 message layout:
        # <PRI>VERSION SP TIMESTAMP SP HOSTNAME SP APP-NAME SP PROCID SP MSGID SP STRUCTURED-DATA [SP MSG]
        header = f"<{priority}>{VERSION} {timestamp} {hostname} {app_name} {procid} {msgid} {structured_data}"
        sysmsg = f"{header} {msg}" if msg else header

        # Upload to ScribeAPI /syslog endpoint
        syslog_url = f"{self.base_url}/syslog"
        body = {"syslog_message": sysmsg}
        response = self.send_post_request(syslog_url, token=self.jwt_token, body=body)
        if response and response.status_code in (200, 204):  # some APIs use 200
            logging.info(f"Syslog event uploaded to ScribeAPI /syslog endpoint.\n{str(body)}")
        else:
            logging.warning(f"Failed to upload syslog event: {getattr(response, 'text', None)} for log {body!r}")

    def get_chache_data(self):
        # Exclude product_list from cache as per requirements
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "datasets": self.datasets,
            "team_name": self.team_name,
            "team_info": self.team_info
        }
    
    def need_cache_data_update(self, cached_data):
        # if timestamp older than one day
        if cached_data and "timestamp" in cached_data:
            try:
                last_update = datetime.datetime.fromisoformat(cached_data["timestamp"])
            except Exception as e:
                logging.error(f"Error parsing timestamp: {e}")
                return True
            return (datetime.datetime.now() - last_update).days > 1
        
    def __init__(self, api_token=None, ignore_env = False, base_url="https://api.scribesecurity.com", refresh_interval=600, cached_data=None, env = "prod",
             username=None, password=None):
    

        def update_from_cached_data(cached_data):
            if "datasets" in cached_data:
                self.datasets = cached_data["datasets"]
                self.dataset_ids = self.create_dataset_id_map(self.datasets)
            else:
                logging.error("No datasets in provided cached data")
            # product_list intentionally not loaded from cache
            if "team_name" in cached_data:
                self.team_name = cached_data["team_name"]
            else:
                logging.error("No team name in provided cached data")
            if "team_info" in cached_data:
                self.team_info = cached_data["team_info"]
            else:
                logging.error("No team info in provided cached data")

        # Default cache file path
        cache_dir = os.path.join(os.getcwd(), ".scribe")
        cache_file = os.path.join(cache_dir, "cache.json")
        loaded_cache = None

        # Only load cache if not explicitly provided
        if cached_data is None:
            try:
                if os.path.exists(cache_file):
                    # Check file age
                    file_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
                    if (datetime.datetime.now() - file_mtime).days <= 1:
                        with open(cache_file, "r") as f:
                            loaded_cache = json.load(f)
                    else:
                        logging.info("Cache file is older than one day, will refresh cache.")
                else:
                    # Ensure .scribe directory exists
                    pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logging.error(f"Error loading cache file: {e}")
        else:
            loaded_cache = cached_data

        if ignore_env:
            self.api_token = api_token
        else:
            self.api_token = api_token or os.getenv('SCRIBE_TOKEN', None)
        if not self.api_token:
            logging.error("No API token provided. Please set the SCRIBE_TOKEN environment variable or pass it as an argument.")
            return
        self.username = username
        self.password = password
        self.env = env
        self.base_url = base_url
        if env != "prod":
            self.base_url = f"https://api.{env}.scribesecurity.com"
        
        if env == "prod":
            self.superset_base_url = "https://superset.scribesecurity.com"
        else:
            if base_url != "https://api.scribesecurity.com":
                env = base_url.split(".")[1]
                self.superset_base_url = f"https://internal-superset.{env}.scribesecurity.com"

        
        self.refresh_interval = refresh_interval
        self.last_refresh = datetime.datetime.now() - datetime.timedelta(days=5)  # Initialize to a time in the past

        self.jwt_token = None
        self.superset_token = None
        self.dataset_ids = None
        self.datasets = None
        self.product_list = None
        self.team_id = None
        self.team_name = None
        self.team_info = None
        p = None
        if self.api_token:
            self.last_refresh = datetime.datetime.now() # - datetime.timedelta(hours=5)
            self.refresh_data(force=True)
            
            # Use loaded_cache if available and not stale, else refresh and save
            if not loaded_cache or self.need_cache_data_update(loaded_cache):
                d = self.get_datasets()
                if not d:
                    logging.error("Refresh: Failed to update dataset IDs")
                else:
                    self.datasets = d
                    self.dataset_ids = self.create_dataset_id_map(d)
                    p = self.get_products(force=True)
                if not p:
                    logging.error("Refresh: Failed to update product list")
                    logging.error(f"Using previous product list\n{self.product_list}")
                else:
                    self.product_list = p

                t = self.get_team_info()
                if not t:
                    logging.error("Failed to get team data.")

                # Save cache (excluding product_list)
                try:
                    pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)
                    cache_data = self.get_chache_data()
                    with open(cache_file, "w") as f:
                        json.dump(cache_data, f, indent=2)
                except Exception as e:
                    logging.error(f"Error saving cache file: {e}")
            else:
                update_from_cached_data(loaded_cache)

    def validate_dataset(self, dataset_name):
        if not self.dataset_ids:
            self.refresh_data()
        if not self.dataset_ids:
            logging.error("Failed to get dataset IDs")
            return False
        if dataset_name not in self.dataset_ids:
            logging.error(f"Dataset {dataset_name} not found")
            return False
        return True
    def set_api_token(self, api_token):
        if self.is_api_token_set():
            return
        self.api_token = api_token
        if self.api_token:
            self.last_refresh = datetime.datetime.now()
            self.refresh_data(force=True)

    def is_api_token_set(self):
        return self.api_token is not None


    def refresh_data(self, force=False):
        if not self.api_token:
            logging.error("No API token provided")
            return
        
        need_refresh = (
            force or
            not self.dataset_ids or
            not self.product_list or
            (datetime.datetime.now() - self.last_refresh).seconds > self.refresh_interval
        )

        if not need_refresh:
            return

        self.last_refresh = datetime.datetime.now()

        self.jwt_token = self.login(self.api_token, self.base_url)
        if not self.jwt_token:
            logging.error("Refresh: Failed to get JWT token")

        try:
            decoded_token = jwt.decode(self.jwt_token, options={"verify_signature": False})
            self.decoded_token = decoded_token
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid JWT token: {e}")
            self.decoded_token = None
            return
        jwt_name = decoded_token.get("name")
        try:
            prefix = "scribe-hub-team" if self.env == "prod" else f"scribe-hub-{self.env}-team"
            self.team_id = jwt_name.split(prefix)[1].split("-")[0]
            logging.info(f"Team:{self.team_id}")
        except Exception as e:
            logging.error(f"Error extracting team ID: {e}")
            self.team_id = None


        self.superset_token = self.get_superset_token(self.jwt_token, self.base_url)
        if not self.superset_token:
            logging.error("Refresh: Failed to get Superset token")

    def send_post_request(self, url, token=None, body=None):
        """
        Deprecated: Use `send_post_request` from `utils.py` instead.
        """
        return send_post_request(url, token, body)

    def send_get_request(self, url, token=None):
        """
        Deprecated: Use `send_get_request` from `utils.py` instead.
        """
        return send_get_request(url, token)

    def decode_jwt_token(self, jwt_token):
        """
        Deprecated: Use `decode_jwt_token` from `utils.py` instead.
        """
        return decode_jwt_token(jwt_token)

    def querystr_to_json(self, query):
        """
        Deprecated: Use `querystr_to_json` from `utils.py` instead.
        """
        return querystr_to_json(query)

    def att2statement(self, data):
        """
        Deprecated: Use `att2statement` from `utils.py` instead.
        """
        return att2statement(data)

    def login(self, api_token, base_url):
        url = f"{base_url}/v1/login"
        body = {"api_token": api_token}
        response = self.send_post_request(url=url, body=body)

        if response and 'token' in response.json():
            return response.json()['token']
        else:
            logging.error("Token not found in the response.")
            return None

    def get_superset_token(self, jwt_token, base_url):
        url = f"{base_url}/dataset/token"
        response = self.send_get_request(url=url, token=jwt_token)
        if not response:
            return None

        response_json = json.loads(response.text)
        if 'access_token' in response_json:
            return response_json['access_token']
        else:
            logging.error("Access token not found in the response.")
            return None

    def create_dataset_id_map(self, datasets):
        data = datasets
        if not data:
            return {}

        try:
            result = data.get("result", [])
            datasource_id_map = {}
            for entry in result:
                datasource_name = entry.get("datasource_name")
                datasource_id = entry.get("id")
                if datasource_name and datasource_id:
                    datasource_id_map[datasource_name] = entry
            return datasource_id_map
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            return {}

    def get_team_info(self):
        if not self.team_id:
            logging.error("Team ID not set.")
            return False
        if not self.validate_dataset(self.scribe_team_stat_dataset):
            return False
        query = {
            "columns": [
                "teamName"
            ],
            "filters": [
                {
                    "col": "teamId",
                    "op": "==",
                    "val": self.team_id
                }
            ],
            "metrics": [],
            "orderby": [],
            "row_limit": 1
        }
        r = self.query_superset(self.scribe_team_stat_dataset, query)
        try:
            self.team_name = r["result"][0]["data"][0]["teamName"]
            self.team_info = r["result"][0]["data"][0]
        except (KeyError, IndexError) as e:
            logging.error(f"Error accessing response data: {e}")
            return False
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            return False

        return True
    
    def get_link(self, use = "products", text = "Link", params = {}):
        params_str = ""
        if params:
            # %3B is the URL encoded version of ';'
            params_str = ";;".join([f"{k}:{v}" for k, v in params.items()])
            params_str = "searchFilters=" + params_str

        if use == "products":
            return f"\n[{text}](https://scribe-security.github.io/redirect/redirect.html?path=%2Fproducer-products)"
        # Add here elif for all uses
        elif use == "product_vulnerabilities":
            if params:
                params_str = '&' + params_str
            # return f"\n[{text}](http://localhost:8090/redirect.html?path=%2Fsbom?redirectTabName=Vulnerabilities&{params_str})"
            return f"\n[{text}](https://scribe-security.github.io/redirect/redirect.html?path=%2Fsbom?redirectTabName=Vulnerabilities{params_str})"
        elif use == "product_policy_results":
            if params:
                params_str = '?' + params_str
            return f"\n[{text}](https://scribe-security.github.io/redirect/redirect.html?path=%2Fpolicy%2Fevaluation{params_str})"
        else:
            return f"\n[{text}](https://app.scribesecurity.com)"

    def get_products(self, all_versions=False, force=False):
        if not force:
            if (datetime.datetime.now() - self.last_refresh).seconds < self.refresh_interval and self.product_list:
                return self.product_list
        if not self.validate_dataset(self.scribe_products_dataset):
            return None

        url = f"{self.base_url}/dataset/data"
        body = {
            "superset_token": self.superset_token,
            "validate": False,
            "query": {
                "datasource": {
                    "id": self.dataset_ids[self.scribe_products_dataset]["id"],
                    "type": "table"
                },
                "force": "false",
                "queries": [
                    {
                        "columns": [
                            "logical_app",
                            "logical_app_version",
                            "version_timestamp"
                        ],
                        "filters": [],
                        "metrics": [],
                        "orderby": [["logical_app", True], ["version_timestamp", False]],
                        "row_limit": 0
                    }
                ],
                "result_format": "json",
                "result_type": "results"
            }
        }

        r = self.send_post_request(url=url, token=self.jwt_token, body=body)
        if not r:
            return self.product_list

        try:
            o = r.json()
            o = convert_timestamps(o, "version_timestamp")
            result = []
            for product in o["result"][0]["data"]:
                item = {"name": product["logical_app"], "version": product["logical_app_version"], "timestamp": product["version_timestamp"]}
                result.append(item)
            self.product_list = result
        except Exception as e:
            logging.error(f"Error decoding JSON: {e}")
            return self.product_list

        if all_versions:
            return result

        # Keep only latest version per product
        latest = []
        last_product = ""
        for product in result:
            if product['name'] == last_product:
                continue
            last_product = product['name']
            latest.append(product)

        # sort by timestamp
        latest.sort(key=lambda x: x['timestamp'], reverse=True)
 
        return latest

    def format_table(self, headers, rows):
        """
        Format a table with aligned columns for better readability in plain text.

        Parameters:
            headers (list): List of column headers.
            rows (list of lists): List of rows, where each row is a list of column values.

        Returns:
            str: Formatted table as a string.
        """
        # Calculate the maximum width of each column
        column_widths = [len(header) for header in headers]
        for row in rows:
            for i, value in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(value)))

        # Create a format string for each row
        row_format = " | ".join(f"{{:<{width}}}" for width in column_widths)

        # Format the header and rows
        header_line = row_format.format(*headers)
        separator_line = "-+-".join("-" * width for width in column_widths)
        row_lines = [row_format.format(*[str(value) for value in row]) for row in rows]

        # Combine all parts into a single string
        return "\n".join([header_line, separator_line] + row_lines)

    def format_query_result_table(self, query_result):
        """
        Format query results into an aligned table for better readability.

        Parameters:
            query_result (dict): The query result containing columns and data.

        Returns:
            str: Formatted table as a string.
        """
        try:
            data = query_result["result"][0]["data"]
            if not data:
                return "No data found"

            columns = query_result["result"][0]["colnames"]
            if not columns:
                return "No columns information found"

            # Prepare headers and rows for the table
            headers = columns
            rows = [[row[col] for col in columns] for row in data]

            # Format the table using the existing format_table method
            return self.format_table(headers, rows)

        except Exception as e:
            logging.error(f"Error formatting query result: {e}")
            return "Error formatting query result"

    def get_products_str(self, with_link=True):
        r = self.get_products()
        if not r:
            return "No products found"

        try:
            # Prepare headers and rows for the table
            headers = ["App", "Version", "Version Timestamp"]
            rows = [[row['name'], row['version'], row['timestamp']] for row in r]

            # Format the table
            table = self.format_table(headers, rows)

            if with_link:
                table += self.get_link(use="products", text="Product page")

        except Exception as e:
            logging.error(f"Error decoding JSON: {e}")
            table = "Error getting product list"

        logging.info(table)
        return table

    def get_logical_app_version(self, logical_app):
        if not self.product_list:
            self.refresh_data()
            if not self.product_list:
                return "I have issues getting data from Scribe, Sorry"
        for product in self.product_list:
            if product["name"] == logical_app:
                latest = product["version"]
                logging.info(f"Latest version for {logical_app} is {latest}")
                return latest
        return None

    def get_product_vulnerabilities(self, logical_app, logical_app_version=None):
        self.refresh_data()
        if not logical_app_version:
            v = self.get_logical_app_version(logical_app)
            if v:
                logical_app_version = v
            else:
                logging.error(f"Failed to get version for {logical_app}")
                return None, None

        if not self.validate_dataset(self.scribe_vulnerabilities_dataset):
            return None
        url = f"{self.base_url}/dataset/data"
        body = {
            "superset_token": self.superset_token,
            "validate": False,
            "query": {
                "datasource": {
                    "id": self.dataset_ids[self.scribe_vulnerabilities_dataset]["id"],
                    "type": "table"
                },
                "force": False,
                "queries": [
                    {
                        "columns": [
                            "vulnerability_id",
                            "severity",
                            "epssProbability",
                            "targetName",
                            "component_name",
                            "logical_app",
                        ],
                        "filters": [
                            {
                                "col": "logical_app",
                                "op": "==",
                                "val": logical_app
                            },
                            {
                                "col": "logical_app_version",
                                "op": "==",
                                "val": logical_app_version
                            },
                            {
                                "col": "vulnerability_id",
                                "op": "like",
                                "val": "CVE-%"
                            }
                        ],
                        "metrics": [],
                        "orderby": [["severity", False], ["epssProbability", False]],
                        "row_limit": 10
                    }
                ],
                "result_format": "json",
                "result_type": "results"
            },
            "validate": False
        }

        r = self.send_post_request(url=url, token=self.jwt_token, body=body)
        if r:
            try:
                return r.json(), logical_app_version
            except Exception as e:
                logging.error(f"Error decoding JSON: {e}")
                return {}, logical_app_version
        return {}, logical_app_version

    def get_product_vulnerabilities_str(self, logical_app, logical_app_version=None, with_link=True):
        r, logical_app_version = self.get_product_vulnerabilities(logical_app, logical_app_version)
        if not r:
            return "Failed getting vulnerability data"

        try:
            vuln_list = r["result"][0]["data"]
            if not vuln_list:
                return "No vulnerabilities found"

            # Prepare headers and rows for the table
            headers = ["ID", "Severity", "EPSS", "Vulnerable Component", "Artifact"]
            rows = [
                [
                    f"[{vuln['vulnerability_id']}](https://nvd.nist.gov/vuln/detail/{vuln['vulnerability_id']})",
                    vuln['severity'],
                    vuln['epssProbability'],
                    vuln['component_name'],
                    vuln['targetName']
                ]
                for vuln in vuln_list
            ]

            # Format the table
            table = self.format_table(headers, rows)

            if with_link:
                table += self.get_link(
                    use="product_vulnerabilities",
                    text="Product vulnerabilities",
                    params={"product": logical_app, "product_version": logical_app_version, "show_file_components": "false"}
                )

        except Exception as e:
            logging.error(f"Error decoding JSON: {e}")
            table = "Error getting vulnerability list"

        logging.info(table)
        return table

    def get_product_vulnerability_distribution(self, logical_app, logical_app_version=None):
        def severity_label(severity):
            print(f"Assigning severity label for severity: {severity}")
            if severity <= 3.9:
                return "Low"
            elif severity <= 6.9:
                return "Medium"
            elif severity <= 8.9:
                return "High"
            else:
                return "Critical"
            
        self.refresh_data()
        if not logical_app_version:
            v = self.get_logical_app_version(logical_app)
            if v:
                logical_app_version = v
            else:
                return None

        if not self.validate_dataset(self.scribe_vulnerabilities_dataset):
            return None
        url = f"{self.base_url}/dataset/data"

        body = {
            "superset_token": self.superset_token,
            "validate": False,
            "query": {
                "datasource": {
                    "id": self.dataset_ids[self.scribe_vulnerabilities_dataset]["id"],
                    "type": "table"
                },
                "force": False,
                "queries": [
                    {
                        "columns": [
                            "logical_app",
                            "logical_app_version",
                            "vulnerability_id",
                            "severity"
                        ],
                        "filters": [
                            {
                                "col": "logical_app",
                                "op": "==",
                                "val": logical_app
                            },
                            {
                                "col": "logical_app_version",
                                "op": "==",
                                "val": logical_app_version
                            },
                            {
                                "col": "vulnerability_id",
                                "op": "like",
                                "val": "CVE-%"
                            }
                        ],
                        "metrics": [
                            {
                                "label": "vulnerabilities",
                                "expressionType": "SQL",
                                "sqlExpression": "COUNT(DISTINCT vulnerability_id)"
                            },
                        ],
                        "post_processing": [],
                        "groupby": ["severity"],
                        "orderby": [["severity", False]],
                        "row_limit": 10
                    }
                ],
                "result_format": "json",
                "result_type": "results"
            }
        }

        r = self.send_post_request(url=url, token=self.jwt_token, body=body)
        if r:
            try:
                r = r.json()
                data = r["result"][0]["data"]
                for row in data:
                    row["severity_label"] = severity_label(row["severity"])
                return data
            except Exception as e:
                logging.error(f"Error decoding JSON: {e}")
                return []
        return []


    def get_datasets(self):
        url = f"{self.base_url}/dataset"
        body = {
            "superset_token": self.superset_token
        }

        r = self.send_post_request(url=url, token=self.jwt_token, body=body)
        if r:
            r = r.json()
            os.makedirs("tmp", exist_ok=True)  # Ensure the tmp directory exists

            with open("tmp/datasets.json", "w") as f:
                json.dump(r, f)
            
        return r
    
    def query_superset(self, dataset, query, time_tokens=[]):
        dataset_name = dataset
        id = None
        if self.dataset_ids and dataset in self.dataset_ids:
            id = self.dataset_ids[dataset]["id"]
        else:
            logging.error(f"Dataset {dataset} not found in dataset IDs")
            return None
        
        url = f"{self.base_url}/dataset/data"
        body = {
            "superset_token": self.superset_token,
            "validate": False, 
            "query": {
                "datasource": {
                    "id": id,
                    "type": "table"
                },
                "force": "false",
                "queries": [
                    query
                ],
                "result_format": "json",
                "result_type": "results"
            },
            "validate": False
        }

        r = self.send_post_request(url=url, token=self.jwt_token, body=body)
        if r:
            try:
                r = r.json()
                for t in time_tokens:
                    r = convert_timestamps(r, col_substr=t)
                return r
            except Exception as e:
                logging.error(f"Error decoding JSON: {e}")
                return {}
            
    def query_result_to_str(self, header, r):
        if not header:
            header = ""
        try:
            data = r["result"][0]["data"]
            if not data:
                return "No data found"
            columns = r["result"][0]["colnames"]
            if not columns:
                return "No columns information found"
            
            md_table = ["| " + " | ".join(columns) + " |", "| ---" * len(columns) + " |"]
            for row in data:
                md_table.append("| " + " | ".join([str(row[col]) for col in columns]) + " |")
            o = header + '\n' + "\n".join(md_table)
        except Exception as e:
            logging.error(f"Error decoding JSON: {e}")
            o = "Error getting data"

        return o
            
    def query_str(self, dataset, query, header = "Query results:"):
        r = self.query_superset(dataset, query, time_tokens = ["timestamp", "time_evaluated", "Time", "created", "published_on", "LastModified",
                                                               "date_changed", "advisory_modified"])
        if not r:
            return "Failed getting data"
        o = self.query_result_to_str(header,r)
        return o
    
    def get_policy_results(self, logical_app="Scribot", logical_app_version=None, initiative="%"):
        self.refresh_data()
        if not logical_app_version:
            v = self.get_logical_app_version(logical_app)
            if v:
                logical_app_version = v
            else:
                logging.error(f"Failed to get version for {logical_app}")
                return None, None
        if not self.validate_dataset(self.scribe_policy_dataset):
            return None, None

        url = f"{self.base_url}/dataset/data"
        body = {
            "superset_token": self.superset_token,
            "validate": False,
            "query": {
                "datasource": {
                    "id": self.dataset_ids[self.scribe_policy_dataset]["id"],
                    "type": "table"
                },
                "force": "false",
                "queries": [
                    {
                        "columns": [
                            "logical_app",
                            "logical_app_version",
                            "asset_type",
                            "asset_name",
                            "status",
                            "time_evaluated",
                            "initiative_name",
                            "control_name",
                            "rule_name",
                            "message"
                        ],
                        "filters": [
                            # {
                            #     "col": "initiative_name",
                            #     "op": "like",
                            #     "val": initiative
                            # },
                            {
                                "col": "logical_app",
                                "op": "==",
                                "val": logical_app
                            },
                            {
                                "col": "logical_app_version",
                                "op": "==",
                                "val": logical_app_version
                            },
                            {
                                "col": "status",
                                "op": "not in",
                                "val": ['Not Applicable', 'Not Applicable']
                            }
                        ],
                        "metrics": [],
                        "orderby": [],#["time_evaluated", False], ["status", True]],
                        "row_limit": 10
                    }
                ],
                "result_format": "json",
                "result_type": "results"
            }
        }

        r = self.send_post_request(url=url, token=self.jwt_token, body=body)
        if r:
            try:
                r = r.json()
                r = convert_timestamps(r, "time_evaluated")
                return r, logical_app_version
            except Exception as e:
                logging.error(f"Error decoding JSON: {e}")
                return {}, logical_app_version
        return {}, logical_app_version

    def get_policy_results_str(self, logical_app="scribe-platform", logical_app_version=None, initiative="%", with_link = True):
        r, logical_app_version = self.get_policy_results(logical_app, logical_app_version, initiative)
        if not r:
            return "Failed getting policy results"

        o = f"Policy results for {logical_app}:\n"
        try:
            o = self.query_result_to_str(o, r)

        except Exception as e:
            logging.error(f"Error decoding JSON: {e}")
            o = "Error getting policy results"
        return o
    
     
    def get_product_lineage(self, logical_app, logical_app_version=None):
        self.refresh_data()
        if not logical_app_version:
            v = self.get_logical_app_version(logical_app)
            if v:
                logical_app_version = v
            else:
                logging.error(f"Failed to get version for {logical_app}")
                return None, None
        if not self.validate_dataset(self.scribe_policy_dataset):
            return None, None
        # left out columns:
        # "product_id",
        # "version_id",
        # "child_id",
        # "properties",
        query = {
            "columns": [
                "timestamp",
                "logical_app",
                "logical_app_version",
                "platform_name",
                "platform_type",
                "asset_type",
                "asset_name",
                "external_id",
                "uri",
                "owner",
                "path",
                "parent_id",
                "parent_type",
                "parent_name",
                "parent_external_id",
                # "properties"
            ],
            "filters": [
                {
                    "col": "logical_app",
                    "op": "==",
                    "val": logical_app
                },
                {
                    "col": "logical_app_version",
                    "op": "==",
                    "val": logical_app_version
                }
            ],
            "metrics": [],
            "orderby": [["timestamp", False]],
            "annotation_layers": [],
            "row_limit": 100,
            "post_processing": []
        }
        r = self.query_superset(self.scribe_lineage_dataset, query, time_tokens = ["timestamp"])
        # TODO: check in superset prod for more columns
        if r:
            try:
                data = r["result"][0]["data"]
            except Exception as e:
                logging.error(f"Error decoding JSON: {e}")
                return [], logical_app_version
            if not data:
                return [], logical_app_version
            for row in data:
                if row.get("properties"):
                    try:
                        row["properties"] = ast.literal_eval(row["properties"])
                    except Exception as e:
                        logging.error(f"Error decoding properties: {e}")
                        row["properties"] = {}
            return data, logical_app_version
        else:
            return [], logical_app_version

    types_to_position = {
            "organization": 1,
            "repo": 2,
            "branch": 3,
            "workflow": 4,
            "workflow_run": 5,
            "image": 6,
            "pod": 7,
            "namespace": 8

    }

    
    include_fields = [
        "platform_name", "platform_type",
        "asset_name", "asset_type","parent_name", "parent_type"
   ]

    def filter_lineage_data(self, data, include_types=types_to_position, include_fields=include_fields):
        """
        Filter the data to only include records of the specified types
        and remove specified fields.

        Parameters:
            data (list): List of JSON records.
            include_types (set): Asset types to keep.
            include_fields (set): Fields to remove from records.

        Returns:
            list: Filtered data.
        """
        filtered_data = []
        
        for record in data:
            if record.get("asset_type") in include_types:
                # Create a copy to avoid modifying original data
                filtered_record = {key: value for key, value in record.items() if key in include_fields}
                filtered_data.append(filtered_record)
        
        return filtered_data
    
    def list_attestations(self, criteria={}):
        self.refresh_data()
        url = f"{self.base_url}/evidence/list"
        body = criteria
        r = self.send_post_request(url=url, token=self.jwt_token, body=body)
        if r:
            try:
                return r.json()
            except Exception as e:
                logging.error(f"Error decoding JSON: {e}")
        return {}

    def get_attestation(self, attestation_id):
        url = f"{self.base_url}/evidence/{attestation_id}"
        r = self.send_get_request(url=url, token=self.jwt_token)
        if not r:
            return {}
        try:
            o = r.json()
            url = o.get("presigned_url")
            if url:
                response = urllib.request.urlopen(url)
                content = response.read()
                o = json.loads(content)
            
                if 'payload' in o:
                    o = self.att2statement(o)
            else:
                logging.error(f"Presigned URL not found in response")
                return {}
        except Exception as e:
            logging.error(f"Error decoding JSON: {e}")
            return {}
        return o

    def get_latest_attestation(self, criteria={}):
        atts = self.list_attestations(criteria=criteria)
        if not atts:
            return {}
        evidence_list = atts.get("evidences", [])
        if not evidence_list:
            return {}

        evidence_list.sort(key=lambda x: x['context']["timestamp"], reverse=True)
        if not evidence_list:
            return {}
        evidence = evidence_list[0]

        att = self.get_attestation(evidence["id"])
        return att
    
    def query_vulnerabilities(self, querystr, title="") -> str:
        logging.debug(f"Query vulnerabilities with: {querystr}")
        query = self.querystr_to_json(querystr)
        if query:
            r = self.query_superset(self.scribe_vulnerabilities_dataset, query, time_tokens=["timestamp"])
            if r:
                return f"{title}\n{self.format_query_result_table(r)}"
        return "Error running query"

    def query_products(self, querystr, title="") -> str:
        logging.debug(f"Query products with: {querystr}")
        query = self.querystr_to_json(querystr)
        if query:
            r = self.query_superset(self.scribe_products_dataset, query, time_tokens=["timestamp"])
            if r:
                return f"{title}\n{self.format_query_result_table(r)}"
        return "Error running query"

    def get_lineage_graph(self, lineage_data, output_file):
        """
        Generate a lineage graph from the lineage data and save it to the specified output file.
        
        Parameters:
            lineage_data (list): List of lineage records.
            output_file (str): Path to save the generated graph.
        
        Returns:
            str: Full path of the saved graph file.
        """
        if not lineage_data:
            logging.error("No lineage data provided for graph generation.")
            return "Error: No lineage data provided."
        
        full_path_filename = create_lineage_graph(lineage_data, output_file=output_file)
        return full_path_filename
    
    def query_lineage(self, querystr, title="", graph_filename=None) -> str:
        logging.debug(f"Query lineage with: {querystr}")
        query = self.querystr_to_json(querystr)
        if query:
            r = self.query_superset(self.scribe_lineage_dataset, query, time_tokens=["timestamp"])
            if r:
                if graph_filename:
                    required_fields = ["asset_name", "asset_type", "parent_name", "parent_type", "external_id", "parent_external_id", "uri"]
                    columns = query.get("columns", [])
                    if not all(field in columns for field in required_fields):
                        logging.error(f"Query must include the following fields: {', '.join(required_fields)}")
                        return "Error: Query must include required fields for lineage graph generation."
                    
                    lineage_data = r["result"][0]["data"]
                    full_path_filename = create_lineage_graph(lineage_data, output_file=graph_filename)
                    logging.info(f"Lineage graph saved to {full_path_filename}")
                else:
                    logging.warning("No graph filename provided, lineage graph will not be generated.")
                return f"{title}\n{self.format_query_result_table(r)}"
        return "Error running query"
    
    def query_policy_results(self, querystr, title="") -> str:
        logging.debug(f"Query policy results with: {querystr}")
        query = self.querystr_to_json(querystr)
        if query:
            r = self.query_superset(self.scribe_policy_dataset, query, time_tokens=["time_evaluated"])
            if r:
                return f"{title}\n{self.format_query_result_table(r)}"
        return "Error running query"
    
    def query_risk(self, querystr, title="") -> str:
        logging.debug(f"Query risk table with: {querystr}")
        query = self.querystr_to_json(querystr)
        if query:
            r = self.query_superset(self.scribe_risk_dataset, query, time_tokens=["timestamp"])
            if r:
                return f"{title}\n{self.format_query_result_table(r)}"
        return "Error running query"
    
    def query_findings(self, querystr, title="") -> str:
        logging.debug(f"Query finding table with: {querystr}")
        query = self.querystr_to_json(querystr)
        if query:
            r = self.query_superset(self.scribe_findings_dataset, query, time_tokens=["timestamp"])
            if r:
                return f"{title}\n{self.format_query_result_table(r)}"
        return "Error running query"
    
    def superset_authenticate(self):
        if not self.username or not self.password:
            logging.error("Username and password must be provided for Superset login.")
            return False

        login_url = f"{self.superset_base_url}/api/v1/security/login"
        body = {
            "username": self.username,
            "password": self.password,
            "provider": "db",
            "refresh": True
        }

        response = self.send_post_request(login_url, token = None, body=body)
        if not response:
            logging.error("Login failed. No response received.")
            return False

        try:
            result = response.json()
        except json.JSONDecodeError:
            logging.error("Failed to parse login response.")
            return False

        access_token = result.get("access_token")
        if access_token:
            self.jwt_token = access_token
            self.superset_token = access_token
            logging.info("Login successful. Tokens obtained.")
            return True
        else:
            logging.error("Login failed. No access token found.")
            return False
    
    def get_dataset_links(self):
                
        self.superset_authenticate()

        if not self.jwt_token:
            logging.error("No JWT token found. Please authenticate first.")
            return []

        dataset_links = []

        #Use slug to directly fetch the API dashboard's datasets
        dashboard_slug = "api-dashboard"
        datasets_url = f"{self.superset_base_url}/api/v1/dashboard/{dashboard_slug}/datasets"
        logging.info(f"Fetching datasets from {datasets_url}")

        datasets_response = self.send_get_request(datasets_url, token=self.jwt_token)
        if not datasets_response:
            logging.error("Failed to fetch datasets for API dashboard.")
            return []

        try:
            datasets_data = datasets_response.json()
            datasets = datasets_data.get("result", [])

            for dataset in datasets:
                dataset_id = dataset.get("id")
                if dataset_id:
                    link = f"{self.base_url}/explore/?datasource_type=table&datasource_id={dataset_id}"
                    dataset_links.append(link)

        except json.JSONDecodeError as e:
            logging.error(f"Error parsing dataset response: {e}")

        logging.info(f"Total dataset links collected: {len(dataset_links)}")
        return dataset_links


    def get_dataset_data(self, dataset_links, output_file="dataset_metadata.csv"):
        records = []

        for link in dataset_links:
            #Properly parse dataset ID from the URL
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)
            dataset_id_list = query_params.get("datasource_id")
            if not dataset_id_list:
                logging.error(f"Could not find dataset_id in link: {link}")
                continue
            dataset_id = dataset_id_list[0]

            dataset_url = f"{self.superset_base_url}/api/v1/dataset/{dataset_id}"
            logging.info(f"Fetching metadata from {dataset_url}")

            response = self.send_get_request(dataset_url, token=self.jwt_token)
            if not response:
                logging.error(f"Failed to fetch metadata for dataset ID {dataset_id}")
                continue
            try:
                metadata_json = response.json()
                dataset_metadata = metadata_json.get("result", {})
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse metadata JSON for dataset ID {dataset_id}: {e}")
                continue

            verbose_name = dataset_metadata.get("verbose_name")
            if not verbose_name or verbose_name == dataset_metadata.get("table_name"):
                verbose_name = dataset_metadata.get("table_name", "").replace("_", " ").title()

            #Get dataset metadata
            dataset_info = {
                "dataset_id": dataset_metadata.get("id"),
                "catalog": dataset_metadata.get("catalog"),
                "changed_on": dataset_metadata.get("changed_on"),
                "table_name": dataset_metadata.get("table_name"),
                "verbose_name": verbose_name,
                "schema": dataset_metadata.get("schema"),
                "datasource_type": dataset_metadata.get("datasource_type"),
                "description": dataset_metadata.get("description"),
            }

            #Get column metadata
            columns = dataset_metadata.get("columns", [])
            if columns:
                for col in columns:
                    record = dataset_info.copy()
                    record.update({
                        "column_id": col.get("id"),
                        "column_name": col.get("column_name"),
                        "column_verbose_name": col.get("verbose_name") or col.get("column_name", "").replace("_", " ").title(),
                        "column_type": col.get("type"),
                        "groupby": col.get("groupby"),
                        "filterable": col.get("filterable"),
                        "is_dttm": col.get("is_dttm"),
                        "column_description": col.get("description"),
                    })
                    records.append(record)
            else:
                records.append(dataset_info)

        #Write to CSV
        if records:
            fieldnames = [
                "dataset_id", "table_name", "verbose_name", "schema", "catalog",
                "datasource_type", "changed_on", "description",
                "column_id", "column_name", "column_verbose_name", "column_type",
                "groupby", "filterable", "is_dttm", "column_description"
            ]
            fieldnames = [field for field in fieldnames if any(field in rec for rec in records)]

            with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

            logging.info(f"Dataset metadata exported to {output_file}")
        else:
            logging.warning("No dataset metadata exported.")

    def get_dataset_tables_dict(self, tables=[]) -> dict:
        if not self.jwt_token:
            self.superset_authenticate()

        dataset_links = self.get_dataset_links()
        if not dataset_links:
            logging.error("No dataset links found.")
            return {}

        self.get_dataset_data(dataset_links)

        # Load data from the CSV file (generated by get_dataset_data)
        records = []
        try:
            with open("dataset_metadata.csv", mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
        except Exception as e:
            logging.error(f"Failed to load dataset_metadata.csv: {e}")
            return {}

        # Group column data by table name
        table_dict = {}
        for row in records:
            table_name = row.get("table_name")
            if tables and table_name not in tables:
                continue

            if table_name not in table_dict:
                table_dict[table_name] = []

            table_dict[table_name].append({
                "column_name": row.get("column_name", ""),
                "type": row.get("column_type", ""),
                "label": row.get("column_verbose_name") or row.get("column_name", "").replace("_", " ").title(),
                "description": row.get("column_description", "")
            })

        # Add markdown for each table
        for table_name, cols in table_dict.items():
            md_parts = []
            md_parts.append(f"## `{table_name}` Columns\n\n")
            md_parts.append("| Column Name | Label | Type | Description | Like-compliant |\n")
            md_parts.append("|-------------|-------|------|-------------|----------------|\n")
            for col in cols:
                column_name = col["column_name"]
                label = col["label"]
                col_type = col["type"].upper()
                description = col["description"]
                expr = row.get("expression", "") or ""
                if col_type == "STRING" and (" in (" in expr.lower() or " in(" in expr.lower()):
                    like_compliant = False
                else:
                    like_compliant = True
                md_parts.append(
                    f"| `{column_name}` | {label} | {col_type} | {description} | {str(like_compliant)} |\n"
                )
            md_parts.append("\n")
            md_str = "".join(md_parts)
            # Add markdown string to the dict for this table
            # If table_dict[table_name] is a list, convert to dict with 'columns' and 'md'
            table_dict[table_name] = {
                "columns": cols,
                "md": md_str
            }
        return table_dict


    def get_dataset_tables_md(self, tables=[]) -> str:
        if not self.jwt_token:
            self.superset_authenticate()

        dataset_links = self.get_dataset_links()
        if not dataset_links:
            logging.error("No dataset links found.")
            return ""

        self.get_dataset_data(dataset_links)

        # Load data from the CSV file
        records = []
        try:
            with open("dataset_metadata.csv", mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
        except Exception as e:
            logging.error(f"Failed to load dataset_metadata.csv: {e}")
            return ""

        # Group columns by table_name
        table_columns = {}
        for row in records:
            table_name = row.get("table_name")
            if tables and table_name not in tables:
                continue

            if table_name not in table_columns:
                table_columns[table_name] = []

            column_name = row.get("column_name", "")
            col_type = row.get("column_type", "")
            col_type = row.get("column_type", "").upper()
            expr = row.get("expression", "") or ""

            if col_type == "STRING" and (" in (" in expr.lower() or " in(" in expr.lower()):
                like_compliant = False
            else:
                like_compliant = True


            table_columns[table_name].append({
                "column_name": column_name,
                "label": row.get("column_verbose_name") or column_name.replace("_", " ").title(),
                "type": col_type,
                "description": row.get("column_description", ""),
                "like_compliant": str(like_compliant)
            })

        # Build markdown
        md_parts = []
        for table_name, cols in table_columns.items():
            md_parts.append(f"## `{table_name}` Columns\n\n")
            md_parts.append("| Column Name | Label | Type | Description | Like-compliant |\n")
            md_parts.append("|-------------|-------|------|-------------|----------------|\n")

            for col in cols:
                md_parts.append(
                    f"| `{col['column_name']}` | {col['label']} | {col['type']} | "
                    f"{col['description']} | {col['like_compliant']} |\n"
                )
            md_parts.append("\n")

        markdown_output = "".join(md_parts)

        # Write to file
        with open("dataset_tables.md", "w", encoding="utf-8") as f:
            f.write(markdown_output)

        logging.info("Saved table metadata Markdown to dataset_tables.md")
        return markdown_output
    
    def get_dataset_prompt(self, dataset, prompt_template=None):
        """
        Returns a prompt string for the given dataset, using a template.
        - dataset: table name to fetch from docs/dataset_tables.json
        - prompt_template: template string with '{table}' placeholder, or None to load from docs/<dataset>-template.md
        """
        import os
        import json
        # Load table data from docs/dataset_tables.json
        table_json_path = os.path.join("docs", "dataset_tables.json")
        if not os.path.exists(table_json_path):
            raise FileNotFoundError(f"dataset_tables.json not found at {table_json_path}")
        with open(table_json_path, "r", encoding="utf-8") as f:
            tables = json.load(f)
        if dataset not in tables:
            raise ValueError(f"Dataset '{dataset}' not found in dataset_tables.json")
        table_md = tables[dataset].get("md")
        if not table_md:
            raise ValueError(f"No markdown found for dataset '{dataset}' in dataset_tables.json")
        # Load template
        if prompt_template is None:
            template_filename = f"{dataset.replace(' ', '_')}-template.md"
            template_path = os.path.join("docs", template_filename)
            if os.path.exists(template_path):
                with open(template_path, "r", encoding="utf-8") as f:
                    prompt_template = f.read()
            else:
                prompt_template = "{table}"
        # Build prompt
        prompt = prompt_template.replace("{table}", table_md)
        return prompt

    def delete_attestation(self, attestation_id):
        """
        Delete an attestation by its ID using the DELETE /evidence/{file_id} endpoint.
        Returns True if successful, False otherwise. Logs the deletion event.
        """
        try:
            url = f"{self.base_url}/evidence/{attestation_id}"
            response = send_delete_request(url, token=self.jwt_token)
            user = None
            if hasattr(self, "decoded_token") and self.decoded_token:
                user = self.decoded_token.get("name") or self.decoded_token.get("preferred_username")
            
            if response.status_code == 204 or response.status_code == 200:
                logging.info(f"Successfully deleted attestation {attestation_id}")
                event = Event(
                    severity="INFO",
                    messageid="Att-Deletion",
                    message=f"Attestation deleted (attestation_id={attestation_id})",
                    user=user,
                )
                self.log_event(event)
                return True
            else:
                logging.warning(f"Failed to delete attestation {attestation_id}")
                event = Event(
                    severity="WARNING",
                    messageid="Att-Deletion",
                    message=f"Attestation deletion failed (attestation_id={attestation_id})",
                    user=user,
                    metadata={"result": {"status": f"{response.status}"}, "error": f"{response.text}"}
                )
                self.log_event(event)
                return False
            
        except Exception as e:
            logging.warning(f"Error occurred while deleting attestation {attestation_id}: {e}")
            return False