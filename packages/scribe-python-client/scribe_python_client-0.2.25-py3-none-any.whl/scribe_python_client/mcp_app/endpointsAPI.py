import textwrap
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from scribe_python_client.client import ScribeClient
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import *
from pathlib import Path
from contextlib import asynccontextmanager
import logging
import json
import os



load_dotenv()
API_TOKEN = os.getenv("SCRIBE_TOKEN")
client = ScribeClient(api_token=API_TOKEN)
# result = client.get_products()
# logging.info(f"Retrieved products: {result}")

toolDocsPath = Path(__file__).parent / "toolsDescriptions/updatedToolDocs.json"


class QueryResponse(BaseModel):
    status: bool
    status_info: str
    data: str


def get_products_list() -> list:
    result = client.get_products()
    listOfProducts = []
    for i in range(len(result)):
        listOfProducts.append(result[i]["name"])
    return listOfProducts

app = FastAPI()
with open(toolDocsPath, "r") as f:
        tools_str = json.load(f)

def clean_output(text: str) -> str:
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()

@app.post("/LLMPromptGenerator", operation_id="LLMPromptGenerator")
def LLMPromptGenerator(input: str = Query(...), function: str = Query(...)) -> str:
    """
    Generate a structured query payload (columns, filters, metrics, etc.) for a specific tool/function
    based on a user's natural language request and tool documentation.

    This endpoint uses an LLM to interpret the user's query and return a valid JSON payload that can
    be used to call the corresponding tool function.

    Valid Functions are [query_lineage, query_products, query_vulnerabilities, query_policy_results, query_findings, query_risk]
    
    Example input:
    - input: "What are the repositories in my products and components?"
    - function: "query_lineage"
    """

    tool_doc = tools_str[function]

    prompt = textwrap.dedent(f"""
        You are a tool selector and payload generator.
        Given the following tool documentation, generate a valid JSON payload for the tool call.

        TOOL:
        {tool_doc}

        USER QUESTION:
        {input}

        Respond ONLY in this JSON format:
        {{
            "columns": [...],
            "filters": [...],
            "metrics": [...],
            "groupby": [...],
            "orderby": [...],
            "row_limit": <int>
        }}
    """)
    return prompt
        
@app.get("/products")
async def get_products():
    """
    Endpoint: Retrieve a list of products managed in Scribe: Should be called when asked for scribe products or a list of products.

    Args: Nothing

    Returns:
        JSONResponse: Json list of products
    """
    try:
        return client.get_products()
    except Exception as e:
        logging.exception(f"Error in get_products endpoint {e}")

@app.get("/datasets")
async def get_datasets():
    """
    Endpoint: Retrieve all datasets: This should be called when anything about datasets is mentions.

    Args: Nothing

    Returns:
        JSONResponse: Json list of datasets
    """
    try:
        return client.get_datasets()
    except Exception as e:
        logging.exception(f"Error in get_datasets endpoint: {e}")

@app.get("/{product_name}/vulns")
async def get_product_vulnerability(product_name: str):
    """
    Endpoint: Retrieve vulnerabilities for a specific product: This should be called when a specifc product and the user is asking for vulnerabilities.

    Args: product name.

    Returns:
        JSONResponse: Json list of product vulnerabilities
    """
    products = get_products_list()
    if product_name not in products:
        logging.exception(f"Product name: {product_name} is not a valid product")
        raise HTTPException(status_code=404, detail=str("Product not found"))
    try:
        return client.get_product_vulnerabilities(product_name)
    except Exception as e:
        logging.exception(f"Error in get_product_vulnerabilities endpoint: {e}")
    

@app.get("/{product_name}/policy")
async def get_product_policy(product_name: str):
    """
    Endpoint: Retrieve policy for a specific product: This should be called when a specifc product and the user is asking for policy.

    Args: product name.

    Returns: JSONResponse: Json list of product policy
    """
    products = get_products_list()
    if product_name not in products:
        logging.exception(f"Product name: {product_name} is not a valid product")
        raise HTTPException(status_code=404, detail=str("Product not found"))
    try:
        return client.get_policy_results(product_name)
    except Exception as e:
        logging.exception(f"Error in get_policy_results endpoint: {e}")

@app.post("/vulnerabilities", operation_id="query_vulnerabilities", description="Use this tool when you already have a structured JSON query with fields that contain columns, filters, metrics, groupby, orderby, row_limit.")
async def query_vulnerabilities(input: dict):
    """
    Description: To answer questions about vulnerabilities like: What are the vulnerabilities of my product? What are the vulnerabilities of a specific component? What are the vulnerabilities of a specific version of a component? Which products have a specific vulnerability, or a vulnerability with a specificy characteristic (such as has_key)
    This needs a valid query, don't no try to run this function with{}, if no valid query is provided call the tool generate_query
    Valid Query:
    {
        "columns": [...],
        "filters": [...],
        "metrics": [...],
        "groupby": [...],
        "orderby": [...],
        "row_limit": <int>
    }
    """
    response = QueryResponse(
        status=True,
        status_info="Query executed successfully",
        data= ""
    )
    try:
        result_str = client.query_vulnerabilities(json.dumps(input))
        logging.debug(result_str)
        if result_str.startswith("Error"):
            logging.exception("Error in query_vulnerabilities endpoint")
            raise HTTPException(status_code=400, detail=result_str)
        if result_str == f"\nNo data found":
            response.status = False
            response.status_info = "No data found"
        else:
            response.data = result_str
    except HTTPException as he:
        raise he    
    except Exception as e:
        logging.exception(f"Error in query_vulnerabilities endpoint: {e}")
        response.status = False
        response.status_info = str(e)
    return response
 
@app.post("/products", operation_id="query_products", description="Use this tool when you already have a structured JSON query with fields that contain columns, filters, metrics, groupby, orderby, row_limit.")
async def query_products(input: dict):
    """
    Description: To answer questions about products like: what are the/my products? What are the components of my product (the this case use the targetName column!)? What are the depdencieis of my product (search the component_name column)? Note that repositories and namespaces are part of the lineage table.
    This needs a valid query, don't no try to run this function with{}, if no valid query is provided call the tool generate_query
    Valid Query:
    {
        "columns": [...],
        "filters": [...],
        "metrics": [...],
        "groupby": [...],
        "orderby": [...],
        "row_limit": <int>
    }
    """
    response = QueryResponse(
        status=True,
        status_info="Query executed successfully",
        data= ""
    )
    try:
        result_str = client.query_products(json.dumps(input))
        logging.debug(result_str)
        if result_str.startswith("Error"):
            logging.exception("Error in query_products endpoint")
            raise HTTPException(status_code=400, detail=result_str)
        if result_str == f"\nNo data found":
            response.status = False
            response.status_info = "No data found"
        else:
            response.data = result_str
    except HTTPException as he:
        raise he    
    except Exception as e:
        logging.exception(f"Error in query_products endpoint: {e}")
        response.status = False
        response.status_info = str(e)
    return response

@app.post("/policy", operation_id="query_policy_results", description="Use this tool when you already have a structured JSON query with fields that contain columns, filters, metrics, groupby, orderby, row_limit.")
async def query_policy_results(input: dict):
    """
    Description: To answer questions about policy evaluations like: What are the policy rules used? or Which of my products has SSDF policy violations? or List policy violations for a product.
    This needs a valid query, don't no try to run this function with{}, if no valid query is provided call the tool generate_query
    Valid Query:
    {
        "columns": [...],
        "filters": [...],
        "metrics": [...],
        "groupby": [...],
        "orderby": [...],
        "row_limit": <int>
    }
    """
    response = QueryResponse(
        status=True,
        status_info="Query executed successfully",
        data= ""
    )
    try:
        result_str = client.query_policy_results(json.dumps(input))
        logging.debug(result_str)
        if result_str.startswith("Error"):
            logging.exception("Error in query_policy_results endpoint")
            raise HTTPException(status_code=400, detail=result_str)
        if result_str == f"\nNo data found":
            response.status = False
            response.status_info = "No data found"
        else:
            response.data = result_str
    except HTTPException as he:
        raise he    
    except Exception as e:
        logging.exception(f"Error in query_policy_results endpoint: {e}")
        response.status = False
        response.status_info = str(e)
    return response
    
@app.post("/lineage", operation_id="query_lineage", description="Use this tool when you already have a structured JSON query with fields that contain columns, filters, metrics, groupby, orderby, row_limit.")
async def query_lineage(input: dict):
    """
    Description: To answer software-factory related questions such as: What repos (or code repositories) are related/part of a product? or What are all the software-factory related components of a product (in this case query for asset_type and asset_name for the logical_app and logical_app_version)?
    This needs a valid query, don't no try to run this function with{}, if no valid query is provided call the tool generate_query
    Valid Query:
    {
        "columns": [...],
        "filters": [...],
        "metrics": [...],
        "groupby": [...],
        "orderby": [...],
        "row_limit": <int>
    }
    """
    response = QueryResponse(
        status=True,
        status_info="Query executed successfully",
        data= ""
    )
    try:
        result_str = client.query_lineage(json.dumps(input))
        logging.debug(result_str)
        if result_str.startswith("Error"):
            logging.exception("Error in query_lineage endpoint")
            raise HTTPException(status_code=400, detail=result_str)
        if result_str == f"\nNo data found":
            response.status = False
            response.status_info = "No data found"
        else:
            response.data = result_str
    except HTTPException as he:
        raise he    
    except Exception as e:
        logging.exception(f"Error in query_lineage endpoint: {e}")
        response.status = False
        response.status_info = str(e)
    return response

@app.post("/risk", operation_id="query_risk", description="Use this tool when you already have a structured JSON query with fields that contain columns, filters, metrics, groupby, orderby, row_limit.")
async def query_risk(input: dict):
    """
    Description: To answer questions about products like: what are the/my products? What are the components of my product (the this case use the targetName column!)? What are the depdencieis of my product (search the component_name column)? Note that repositories and namespaces are part of the lineage table.
    This needs a valid query, don't no try to run this function with{}, if no valid query is provided call the tool generate_query
    Valid Query:
    {
        "columns": [...],
        "filters": [...],
        "metrics": [...],
        "groupby": [...],
        "orderby": [...],
        "row_limit": <int>
    }
    """
    response = QueryResponse(
        status=True,
        status_info="Query executed successfully",
        data= ""
    )
    try:
        result_str = client.query_risk(json.dumps(input))
        logging.debug(result_str)
        if result_str.startswith("Error"):
            logging.exception("Error in query_risk endpoint")
            raise HTTPException(status_code=400, detail=result_str)
        if result_str == f"\nNo data found":
            response.status = False
            response.status_info = "No data found"
        else:
            response.data = result_str
    except HTTPException as he:
        raise he    
    except Exception as e:
        logging.exception(f"Error in query_risk endpoint: {e}")
        response.status = False
        response.status_info = str(e)
    return response

@app.post("/findings", operation_id="query_findings", description="Use this tool when you already have a structured JSON query with fields that contain columns, filters, metrics, groupby, orderby, row_limit.")
async def query_findings(input: dict):
    """
    Description: Use this function to answer questions about security findings from tools, such as severities, CWE types, affected components, or file locations. Use it when asking about issues found in scans, their severity, tool origin, or impacted products.
    This needs a valid query, don't no try to run this function with{}, if no valid query is provided call the tool generate_query
    Valid Query:
    {
        "columns": [...],
        "filters": [...],
        "metrics": [...],
        "groupby": [...],
        "orderby": [...],
        "row_limit": <int>
    }
    """
    response = QueryResponse(
        status=True,
        status_info="Query executed successfully",
        data= ""
    )
    try:
        result_str = client.query_findings(json.dumps(input))
        logging.debug(result_str)
        if result_str.startswith("Error"):
            logging.exception("Error in query_findings endpoint")
            raise HTTPException(status_code=400, detail=result_str)
        if result_str == f"\nNo data found":
            response.status = False
            response.status_info = "No data found"
        else:
            response.data = result_str
    except HTTPException as he:
        raise he    
    except Exception as e:
        logging.exception(f"Error in query_findings endpoint: {e}")
        response.status = False
        response.status_info = str(e)
    return response