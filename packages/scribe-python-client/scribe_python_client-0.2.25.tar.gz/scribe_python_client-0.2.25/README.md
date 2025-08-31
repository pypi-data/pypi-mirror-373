---
title: Scribe MCP
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Scribe Python Client

The Scribe Python Client is a library for interacting with the ScribeHub API. It provides a simple interface for accessing datasets, querying vulnerabilities, and managing products.

## Installation

Install the package using pip:

```bash
pip install scribe-python-client
```

### Installation Options

The Scribe Python Client supports several installation options for additional features:

- **Base install**: Installs the core client.
  ```bash
  pip install scribe-python-client
  ```
- **MCP support**: Installs the client with Model Context Protocol (MCP) server support and its dependencies.
  ```bash
  pip install "scribe-python-client[mcp]"
  ```
- **Graph support**: Installs the client with graph and visualization dependencies (for lineage graph and related features).
  ```bash
  pip install "scribe-python-client[graph]"
  ```
- **All features**: Installs the client with all optional dependencies (including MCP, graph, and any future extras).
  ```bash
  pip install "scribe-python-client[all]"
  ```

Use the appropriate option depending on your needs:
- If you only require the basic API/CLI, the base install is sufficient.
- For advanced features like the MCP server, use the `[mcp]` or `[all]` options.
- For graph/visualization features (e.g., lineage graph), use the `[graph]` or `[all]` options.

## Usage
The client requires an API token for authentication. You can obtain your API token from the ScribeHub dashboard.
The CLI supports providing the `SCRIBE_TOKEN` as an argument, `--api-key`. You can set the `SCRIBE_TOKEN` environment variable to avoid passing the `--api_token` argument:

```bash
export SCRIBE_TOKEN=YOUR_API_TOKEN
scribe-client --api_call get-products
```

### CLI Usage

The package includes a CLI tool for quick interactions. After installation, you can use the `scribe-client` command. Below are examples for all supported commands:

### Examples

#### Get Products
Retrieve a list of products managed in Scribe:
```bash
scribe-client --api-call get-products --api-token YOUR_API_TOKEN
```
#### Get Product Vulnerabilities
Retrieve vulnerabilities for a specific product:
```bash
scribe-client --api-call get-product-vulnerabilities --product-name YOUR_PRODUCT_NAME --api-token YOUR_API_TOKEN
```

#### Get Policy Results
Retrieve policy results for a specific product:
```bash
scribe-client --api-call get-policy-results --product-name YOUR_PRODUCT_NAME --api-token YOUR_API_TOKEN
```

#### Get Datasets
Retrieve all datasets:
```bash
scribe-client --api-call get-datasets --api-token YOUR_API_TOKEN
```

#### List Attestations
List all attestations:
```bash
scribe-client --api-call list-attestations --api-token YOUR_API_TOKEN
```
#### Get Attestation
Retrieve a specific attestation by ID:
```bash
scribe-client --api-call get-attestation --attestation-id YOUR_ATTESTATION_ID --api-token YOUR_API_TOKEN
```
Attestation IDs ca n be obtained from the list of attestations - search for 'id' in the output.

#### Get Latest Attestation
Retrieve the latest attestation for a specific product:
```bash
scribe-client --api-call get-latest-attestation --product-name YOUR_PRODUCT_NAME --api-token YOUR_API_TOKEN
```

## Specific Dataset Commands

The Scribe Python Client allows you to interact with specific datasets for advanced queries and data retrieval. Below are details about these commands and examples of how to use them.

### Querying Specific Datasets

You can query specific datasets such as vulnerabilities, products, policies, and lineage. These commands allow you to run custom queries and retrieve detailed information.

#### Query Vulnerabilities Dataset
Run a custom query on the vulnerabilities dataset:
```bash
scribe-client --api-call query-vulnerabilities --query "{\"columns\": [\"vulnerability_id\", \"severity\"], \"filters\": [{\"col\": \"severity\", \"op\": \"==\", \"val\": \"High\"}], \"orderby\": [], \"row_limit\": 10}"
```

#### Query Products Dataset
Run a custom query on the products dataset:
```bash
scribe-client --api-call query-products --query "{\"columns\": [\"logical_app\", \"logical_app_version\"], \"filters\": [{\"col\": \"logical_app\", \"op\": \"like\", \"val\": \"%example%\"}], \"orderby\": [], \"row_limit\": 5}"
```

#### Query Policy Results Dataset
Run a custom query on the policy results dataset:
```bash
scribe-client --api-call query-policy-results --query "{\"columns\": [\"status\", \"time_evaluated\"], \"filters\": [{\"col\": \"status\", \"op\": \"==\", \"val\": \"Passed\"}], \"orderby\": [], \"row_limit\": 10}"
```

#### Query Lineage Dataset
Run a custom query on the lineage dataset:
```bash
scribe-client --api-call query-lineage --query "{\"columns\": [\"asset_name\", \"asset_type\"], \"filters\": [{\"col\": \"asset_type\", \"op\": \"==\", \"val\": \"repo\"}], \"orderby\": [], \"row_limit\": 10}"
```

Run a custom query on the lineage dataset and create a graph of the lineage:
```bash
scribe-client --api-call query-lineage --query "{\"columns\": [\"asset_name\", \"asset_type\", \"parent_name\", \"parent_type\", \"external_id\", \"parent_external_id\", \"uri\"], \"filters\": [{\"col\": \"logical_app\", \"op\": \"==\", \"val\": \"Astro-Analytics-Discovery\"}, {\"col\": \"logical_app_version\", \"op\": \"==\", \"val\": \"36\"}], \"orderby\": []}" --lineage-graph-file lineage-graph.html
```
Note that the columns in the query are the minimal set required to create a lineage graph. 

### Notes
- Replace the `--query` argument with your desired query in JSON format.
- Ensure that the query structure matches the dataset schema for accurate results.
- Use the `--api-token` argument or set the `SCRIBE_TOKEN` environment variable for authentication.

### Library Usage

You can also use the library programmatically in your Python code:

```python
from scribe_python_client.client import ScribeClient

# Initialize the client
client = ScribeClient(api_token="YOUR_API_TOKEN")

# Get products
products = client.get_products()
print(products)

# Get datasets
datasets = client.get_datasets()
print(datasets)
```

## Features

- **Get Products**: Retrieve a list of products managed in Scribe.
- **Query Datasets**: Query datasets for vulnerabilities, policy results, and more.
- **CLI Support**: Use the `scribe-client` command for quick API interactions.

## Function Groups

The library provides the following hierarchical function groups:

### 1. Product Management
- **Get Products**: Retrieve a list of products managed in Scribe.
- **Get Product Vulnerabilities**: Retrieve vulnerabilities for a specific product.

### 2. Dataset Management
- **Get Datasets**: Retrieve all datasets.
- **Query Datasets**: Query datasets for vulnerabilities, policy results, and more.

### 3. Policy Management
- **Get Policy Results**: Retrieve policy results for a specific product.

### 4. Attestation Management
- **List Attestations**: List all attestations.
- **Get Attestation**: Retrieve a specific attestation by ID.
- **Get Latest Attestation**: Retrieve the latest attestation for a specific product.


## Tables Description
This description is informative only; it may be partial and may change as the API evolves. 

### `query_vulnerabilities` Columns
| Column Name                     | Description                                    |
|---------------------------------|------------------------------------------------|
| `advisory_justification`        | Justification for advisory decision           |
| `advisory_modified`             | Advisory creation timestamp                   |
| `advisory_status`               | Advisory decision status                      |
| `advisory_text`                 | Additional advisory information               |
| `attestation_ids`               | IDs for SBOM attestations                     |
| `attestation_name`              | SBOM attestation name                         |
| `base_score`                    | CVSS base score                               |
| `component_id`                  | Dependency ID                                 |
| `component_locations`           | Dependency locations in the product           |
| `component_name`                | Dependency name                               |
| `component_purl`                | Dependency Package URL                        |
| `component_version`             | Dependency version                            |
| `cvss_score`                    | CVSS score                                    |
| `epssProbability`               | Exploitability probability                    |
| `final_severity`                | Updated severity by user                      |
| `has_fix`                       | Is a patch available?                         |
| `has_kev`                       | Known Exploited Vulnerability?                |
| `id`                            | ID                                            |
| `is_latest_logical_version`     | Is this the latest product version?           |
| `labels`                        | User-defined labels for SBOM                  |
| `logical_app`                   | Product name                                  |
| `logical_app_version`           | Product version                               |
| `severity`                      | Original severity (integer, cvss score)       |
| `source_layer`                  | Image layer source of vulnerability           |
| `targetName`                    | Container/component name                      |
| `vector`                        | CVSS vector                                   |
| `version_timestamp`             | Timestamp of version                          |
| `vul_component_created`         | Dependency creation date                      |
| `vul_component_fixed_in_versions` | Fixed versions for the vulnerability        |
| `vul_published_on`              | Vulnerability publication date                |
| `vulnerability_id`              | Vulnerability ID (e.g., CVE-2024-5535)        |

### `query_products` Columns

When a user says component he means a container, and when he says dependency he means what the table calls components.
All conditions should be in the filter part, NOT in the group by.

| Column Name            | Description                                          |
|------------------------|------------------------------------------------------|
| `base_layer`           | "TRUE" if the dependency is part of the base layer, otherwise "FALSE" |
| `component_name`       | Dependency name                                      |
| `component_purl`       | Dependency URL                                       |
| `component_version`    | Dependency version                                   |
| `license_expression`   | License information                                  |
| `logical_app`          | Product name                                         |
| `logical_app_version`  | Product version                                      |
| `high_severity_cves`   | Count of critical/high vulnerabilities               |
| `labels`               | User-defined labels                                  |
| `version_is_up_to_date`| Is the dependency version up-to-date?                |
| `targetName`           | The name of a part of a products (high level compoenent, like a docker image) |
| `tag`                  | The tag/version of a part of a products (high level compoenent, like a docker image) |

### `query_policy_results` Columns
| Column Name           | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `time_evaluated`      | Timestamp when the policy was evaluated.                                   |
| `logical_app`         | Product name.                                                              |
| `logical_app_version` | Product version.                                                           |
| `initiative_id`       | Identifier for the specific initiative associated with the policy.         |
| `version_id`          | Identifier for the version of the initiative or rule.                      |
| `gen_rule_id`         | Unique identifier for the general rule.                                    |
| `gen_rule_name`       | Name of the general rule.                                                  |
| `status`              | Rule result (e.g., pass, fail).                                            |
| `status_string`       | Detailed textual description of the rule result status.                    |
| `targetName`          | Name of the specific target being evaluated (component)                    |
| `gate`                | Checkpoint where the rule was evaluated.                                   |
| `count`               | Number of results.                                                         |
| `more`                | Additional information or metadata about the evaluation (if available).    |

### `query_lineage` Columns

When asked about products - use the logical_app and logical_app version columns and not the parent_name.

| Column Name           | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `asset_name`         | Name of the asset.                                                          |
| `asset_type`         | Type of the asset (e.g., repo, image, pod).                                 |
| `external_id`        | External identifier for the asset.                                          |
| `logical_app`        | Product name.                                                              |
| `logical_app_version` | Product version.                                                           |
| `owner`              | Owner of the asset, if applicable.                                          |
| `parent_external_id` | External identifier of the parent asset.                                    |
| `parent_id`          | Unique identifier of the parent asset.                                      |
| `parent_name`        | Name of the parent asset.                                                   |
| `parent_type`        | Type of the parent asset.                                                   |
| `path`              | Relative or absolute path to the asset.                                     |
| `platform_name`      | Name of the platform hosting the asset.                                     |
| `platform_type`      | Type of platform (e.g., SCM, namespace).                                    |
| `product_id`        | Unique identifier for the product.                                          |
| `properties`         | Additional properties of the asset, as a json string                       |
| `timestamp`         | Timestamp when the asset was recorded.                                      |
| `uri`               | URI linking to the asset, if available.                                     |


## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.# test



## Superset Table and Metadata Export

The following `--api-call` commands export metadata from Superset:

- `get-dataset-links`
- `get-dataset-data`
- `get-dataset-tables-dict`
- `get-dataset-tables-md`

These commands **require a Superset username and password**, passed via CLI arguments. Example:

```bash
python -m scribe_python_client.cli --api-call get-dataset-tables-md --env dev --username 'your_username' --password 'your_password'
```

## Upload/Update dataset data using yaml_export.py

Log in to Scribe Superset (dev or prod). Go to the **Datasets** tab and search for the dataset you want to export. Click on the dataset name, then select **Export Dataset**. This will download a `.zip` file. Extract its contents. After extracting the zip file, open the `datasets/` folder inside.

Find the `.yaml` file for your dataset.  
Example path:  
`dataset_export_20250729/datasets/your_dataset.yaml`

Open the script at:  
`scribe-python-client/scribe_python_client/yaml_export.py`

Locate the line that sets the `yaml_input_path` variable and update it to point to your YAML file, the CSV file you want to extract from, and update the output file. Then run the script using this command:

```bash
python scribe-python-client/scribe_python_client/yaml_export.py
```

The metadata of the dataset is updated through a Google Sheet [here](https://docs.google.com/spreadsheets/d/1MaUylXeocaeoJueLRRf6GdPAupSW88huCMPQeYjYfz8/edit?usp=sharing). Download it to csv for the update process.


# Scribe Python Client MCP

## Installation

Install the package with MCP support using pip:

```bash
pip install "scribe-python-client[mcp]"
```

## Usage

The client requires two API tokens for authentication:

- **Scribe API token** — Obtain it from the ScribeHub dashboard.
- **OpenAI API token** — Get it from the OpenAI website.

## CLI Usage

The package includes a CLI tool for quick interactions. After installation, you can use the `scribe-client` command with the `--mcp` flag to start the MCP server:

```bash
scribe-client --mcp
```

## Tool Usage

Once the server is started via the CLI:

1. Open the `mcp.json` configuration file.  
2. Start the `ScribeMCPLocal` server.  
3. The tools should then become active and accessible in Copilot.

The MCP server supports all methods through both:  
- Direct REST queries  
- Query generation from natural language questions

## Documentation

Comprehensive documentation is available for all POST endpoints, including:  
- Valid query parameters  
- Allowed columns  
- Query examples  
- Function descriptions


