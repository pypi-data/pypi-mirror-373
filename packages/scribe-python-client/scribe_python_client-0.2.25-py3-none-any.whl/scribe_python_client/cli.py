import argparse
import os
import logging
from .client import ScribeClient
import json

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "mcp_app", "env")  # relative to cli.py location
load_dotenv(dotenv_path)

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Scribe Client CLI")
    parser.add_argument("--api-call", choices=[
        "get-products",
        "get-datasets",
        "get-policy-results",
        "list-attestations",
        "get-attestation",
        "delete-attestation",
        "get-product-vulnerabilities",
        "get-latest-attestation",
        "query-vulnerabilities",
        "query-products",
        "query-policy-results",
        "query-lineage",
        "query-risk",
        "query-findings",
        "get-dataset-links",
        "get-dataset-data",
        "get-dataset-tables-dict",
        "get-dataset-tables-md",
    ], help="Which API call to execute")
    parser.add_argument("--api-token", required=False, default=os.getenv('SCRIBE_TOKEN'), help="Your API token from ScribeHub integrations page (defaults to SCRIBE_TOKEN environment variable)")
    parser.add_argument("--env", default="prod", choices=["prod", "dev", "test", "ci"], help="Which environment to use")
    parser.add_argument("--product-name", required=False, help="The name of the product (required for specific API calls)")
    parser.add_argument("--attestation-id", required=False, help="The ID of the attestation (required for get-attestation API call)")
    parser.add_argument("--query", required=False, help="The query to run on the dataset (required for query commands)")
    parser.add_argument("--lineage-graph-file", required=False, help="The file to save the lineage graph to (optional)")
    parser.add_argument("--username", required=False, default = os.getenv('SUPERSET_DEV_USERNAME'), help="Superset username (required for Superset API calls)")
    parser.add_argument("--password", required=False, default = os.getenv('SUPERSET_DEV_PASSWORD'), help="Superset password (required for Superset API calls)")
    parser.add_argument("--mcp", action="store_true", help="Run the MCP FastAPI server (requires [mcp] extras)")



    args = parser.parse_args()
    if args.mcp:
        import traceback
        try:
            from scribe_python_client.mcp_app.main import run_mcp_server
        except Exception as e:
            logging.error("FastAPI server not available. Install with: pip install scribe-python-client[mcp]")
            traceback.print_exc()
            exit(1)
        run_mcp_server()
        return
    if not args.api_token:
        logging.error("No API token provided. Please set the SCRIBE_TOKEN environment variable or pass --api-token.")
        exit(1)

    if args.api_call in ["get-policy-results", "get-product-vulnerabilities", "get-latest-attestation"] and not args.product_name:
        logging.error("The --product-name argument is required for the selected API call.")
        exit(1)

    if args.api_call in ["get-attestation", "delete-attestation"] and not args.attestation_id:
        logging.error("The --attestation-id argument is required for the selected API call.")
        exit(1)

    if args.api_call in ["query-vulnerabilities", "query-products", "query-policy-results", "query-lineage"] and not args.query:
        logging.error("The --query argument is required for the selected API call.")
        exit(1)

    base_url = "https://api.scribesecurity.com"
    if args.env != "prod":
        base_url = f"https://api.{args.env}.scribesecurity.com"
    
    if args.api_call in ["get-dataset-links", "get-dataset-data", "get-dataset-tables-dict", "get-dataset-tables-md"]:
        if not args.username or not args.password:
            logging.error("--username and --password are required for Superset table export commands.")
            exit(1)

    client = ScribeClient(api_token=args.api_token, base_url=base_url, env = args.env, username= args.username, password=args.password)
    # lineage_prompt = client.get_dataset_prompt(client.scribe_lineage_dataset)
    # print(f"Lineage prompt:\n {lineage_prompt}")
    logging.info(f"Executing API call: {args.api_call}")

    if args.api_call == "get-products":
        print(client.get_products_str())
    elif args.api_call == "get-datasets":
        print(client.get_datasets())
    elif args.api_call == "get-policy-results":
        print(client.get_policy_results_str(logical_app=args.product_name))
    elif args.api_call == "list-attestations":
        print(client.list_attestations())
    elif args.api_call == "get-attestation":
        print(client.get_attestation(args.attestation_id))
    elif args.api_call == "delete-attestation":
        success = client.delete_attestation(args.attestation_id)
        if success:
            print(f"Attestation {args.attestation_id} deleted successfully.")
        else:
            print(f"Failed to delete attestation {args.attestation_id}.")
    elif args.api_call == "get-product-vulnerabilities":
        print(client.get_product_vulnerabilities_str(logical_app=args.product_name))
    elif args.api_call == "get-latest-attestation":
        criteria = {"name": args.product_name}
        print(client.get_latest_attestation(criteria=criteria))
    elif args.api_call == "query-vulnerabilities":
        print(client.query_vulnerabilities(querystr=args.query))
    elif args.api_call == "query-products":
        print(client.query_products(querystr=args.query))
    elif args.api_call == "query-policy-results":
        print(client.query_policy_results(querystr=args.query))
    elif args.api_call == "query-lineage":
        print(client.query_lineage(querystr=args.query))
        if args.lineage_graph_file:
            client.query_lineage(args.query, graph_filename=args.lineage_graph_file)
            # logging.info(f"Lineage graph saved to {args.lineage_graph_file}")
    elif args.api_call == "query-risk":
        print(client.query_risk(querystr=args.query))
    elif args.api_call == "query-findings":
        print(client.query_findings(querystr=args.query))

    # Get dataset metadata section:
    elif args.api_call == "get-dataset-links":
        links = client.get_dataset_links()
        if links:
            print("Dataset Links:")
            for link in links:
                print(link)
        else:
            logging.error("No dataset links found.")
        result = None
    elif args.api_call == "get-dataset-data":
        dataset_links = client.get_dataset_links()
        if dataset_links:
            client.get_dataset_data(dataset_links, output_file="dataset_metadata.csv")
            logging.info("Metadata export completed successfully.")
        else:
            logging.error("No dataset links found.")
        result = None
    elif args.api_call == "get-dataset-tables-dict": 
        dataset_links = client.get_dataset_links()
        if dataset_links:
            client.get_dataset_data(dataset_links, output_file="dataset_metadata.csv")
            logging.info("Metadata export completed successfully.")
        else:
            logging.error("No dataset links found.")
        result = None

        tables_dict = client.get_dataset_tables_dict()
        #Output path is set to docs/dataset_tables.json
        output_path = os.path.join("docs", "dataset_tables.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(tables_dict, f, indent=2)

        logging.info(f"Saved table metadata dictionary to {output_path}")

        if result is not None:
            print(result)
    elif args.api_call == "get-dataset-tables-md":
        if not client.jwt_token:
            username = input("Enter your Superset username: ")
            password = input("Enter your Superset password: ")
            client.username = username
            client.password = password
            if not client.authenticate():
                logging.error("Superset login failed.")
                exit(1)
        dataset_links = client.get_dataset_links()
        if dataset_links:
            client.get_dataset_data(dataset_links, output_file="dataset_metadata.csv")
            md_output = client.get_dataset_tables_md()
            #Output path is set to docs/dataset_tables.md
            output_path = os.path.join("docs", "dataset_tables.md")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_output)
            logging.info(f"Saved table metadata Markdown to {output_path}")
        else:
            logging.error("No dataset links found.")

if __name__ == "__main__":
    main()