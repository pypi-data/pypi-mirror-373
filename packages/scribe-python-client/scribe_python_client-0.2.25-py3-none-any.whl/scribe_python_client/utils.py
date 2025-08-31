import datetime
import json
import logging
import requests
import urllib
import base64

def convert_timestamps(data, col_substr="timestamp"):
    """
    Recursively convert all fields containing 'timestamp' in their key
    from epoch-milliseconds to UTC ISO8601 formatted strings.
    """
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if col_substr in k and isinstance(v, (int, float)):
                ts_seconds = v / 1000.0
                dt = datetime.datetime.fromtimestamp(ts_seconds)
                new_data[k] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                new_data[k] = convert_timestamps(v, col_substr=col_substr)
        return new_data

    elif isinstance(data, list):
        return [convert_timestamps(item, col_substr=col_substr) for item in data]

    return data

def send_post_request(url, token=None, body=None):
    try:
        headers = {}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'

        logging.debug(f"Sending POST request to {url} with body: {json.dumps(body, indent=2)}")

        response = requests.post(url=url, headers=headers, json=body)

        if response.status_code == 200 or response.status_code == 204:
            logging.info(f"POST request to {url} successful with status code: {response.status_code}")
            return response
        else:
            logging.warning(f"POST request to {url} failed with status code: {response.status_code}, {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return None

def send_get_request(url, token=None):
    try:
        headers = {}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            logging.info(f"GET request from {url} successful with status code: {response.status_code}")
            return response
        else:
            logging.warning(f"GET request from {url} failed with status code: {response.status_code}\n{response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return None
    
def send_delete_request(url, token=None):
    try:
        headers = {}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'

        response = requests.delete(url=url, headers=headers)

        if response.status_code == 204 or response.status_code == 200:
            logging.info(f"DELETE request to {url} successful with status code: {response.status_code}")
            return response
        else:
            logging.warning(f"DELETE request to {url} failed with status code: {response.status_code}, {response.text}")
            return response

    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        return None

def decode_jwt_token(jwt_token):
    try:
        return json.loads(base64.b64decode(jwt_token.split(".")[1] + "=="))
    except Exception as e:
        logging.error(f"Error decoding JWT token: {e}")
        return None

def querystr_to_json(query):
    """
    Convert a query string to a JSON object.

    Parameters:
        query (str): The query string to convert.

    Returns:
        dict: The JSON object representation of the query string.
    """
    try:
        return json.loads(query)
    except Exception as e:
        logging.error(f"Error loading query: {e}\n{query}")
        return {}

def att2statement(data):
    """
    Decode an attestation payload into a statement.

    Parameters:
        data (dict): The attestation data containing a base64-encoded payload.

    Returns:
        dict: The decoded statement.
    """
    try:
        payload_base64 = data['payload']
        payload_decoded = base64.b64decode(payload_base64)
        payload_json = json.loads(payload_decoded)

        inner_payload_base64 = payload_json['payload']
        inner_payload_decoded = base64.b64decode(inner_payload_base64)

        inner_payload_decoded_str = inner_payload_decoded.decode('utf-8')
        final_json = json.loads(inner_payload_decoded_str)
        return final_json

    except Exception as e:
        logging.error(f"Error decoding JSON: {e}")
        return {}