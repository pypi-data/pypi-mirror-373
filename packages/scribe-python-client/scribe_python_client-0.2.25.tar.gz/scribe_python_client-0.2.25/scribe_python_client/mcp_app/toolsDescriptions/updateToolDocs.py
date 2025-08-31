from collections import defaultdict
from pathlib import Path
import json


fullToolDocs = Path(__file__).parent / "fullToolDocs/full_tool_docs.json"
queryExamples = Path(__file__).parent / "fullToolDocs/queryExamples.json"
queryParams = Path(__file__).parent / "fullToolDocs/queryParams.json"
queryDescription = Path(__file__).parent / "fullToolDocs/queryDescription.json"
queryTables = Path(__file__).parent / "fullToolDocs/queryTables.json"
functionDocumention = Path(__file__).parent / "fullToolDocs/functionDocumention.json"
retrieveTables = Path(__file__).parent.parent.parent.parent / "docs/dataset_tables.json"
updatedToolDocs = Path(__file__).parent / "updatedToolDocs.json"

endpoints = {"query_lineage": "extended_lineage_new", "query_policy_results": "policy_initiative","query_products": "asbom_filtered","query_risk": "product_risk_1.0", "query_vulnerabilities": "API Vulnerabilities", "query_findings": "Findings"}


def addExample(function: str, question: str, querystr):
    """
    The function can accept querystr as either a JSON object (dict) or a string. If using a JSON object, set format="json"; otherwise, the default is to treat querystr as a plain string.
    """
    try: 
        with open(queryExamples, "r+") as f:
            data = json.load(f)
    except:
        data = {}
    if function not in endpoints.keys(): raise "Not a valid function"
    try: 
        querystr = json.loads(querystr)
    except:
        pass
    if function not in data: data[function] = []
    for i in range(len(data[function])): 
        if data[function][i]["input"] == question: return 
    data[function].append({"input": question,"output": querystr})
    with open(queryExamples, "w") as f:
        json.dump(data, fp=f, indent=2)

def addDescription(function: str, description: str):
    with open(queryDescription, "r+") as f:
        data = json.load(f)
        data[function] = description
    with open(queryDescription, "w") as f:
        json.dump(data, fp=f, indent=2)

def getDescription(function: str):
    with open(queryDescription, "r+") as f:
        data = json.load(f)
    return data[function]

def updateTables():
    with open(retrieveTables, "r") as f:
        data = json.load(f)
        tables = {}
        for key, value in endpoints.items():
            del data[value]["md"]
            tables[key] = data[value]
    with open(queryTables, "w") as f:
        json.dump(tables, fp=f, indent=2)

def getTables(key: str):
    with open(retrieveTables, "r") as f:
        res = []
        data = json.load(f)
        for item in data[key]["columns"]:
            res.append((item["column_name"], item["description"]))
    return res

def updateFullToolDescription():
    with open(queryExamples, "r") as f: 
        examples = json.load(f)
    with open(queryParams, "r") as f: 
        params = json.load(f)
    with open(queryDescription, "r") as f: 
        descriptions = json.load(f)
    with open(queryTables, "r") as f: 
        tables = json.load(f)
    endpointDocumention = defaultdict(list)
    with open(fullToolDocs, "w") as f:
        for endpoint in endpoints.keys():
            endpointDocumention[endpoint].append({"name": endpoint})
            endpointDocumention[endpoint].append({"description": descriptions[endpoint]})
            endpointDocumention[endpoint].append({"params": params})
            endpointDocumention[endpoint].append({"examples": examples[endpoint]})
            endpointDocumention[endpoint].append({"ColumnTables": tables[endpoint]})
        json.dump(endpointDocumention, fp=f, indent=2)

def parseDoc(): 
    with open(functionDocumention, "r") as f:
        data = json.load(f)
        name, description, tableName = data["name"], data["description"], data["tableName"] 
        endpoints[name] = tableName
        for item in data["examples"].values():
            addExample(function=name, question=item["question"], querystr=item["querystr"])
        addDescription(name, description=description)
        updateTables()
    updateFullToolDescription()


def writeUpdateToolDocs():
    args = {"args": {"columns": [], "filters": [], "metrics": [], "groupby": [], "orderby": [], "row_limit": 20}, "instructions": "Output ONLY the JSON object with no extra text, keep Querys as simple as possible while still including all relvant info. If the query mentions querying a specific table—like the vulnerabilities table—or requests something like the lineage graph, the function called should correspond to that specific query."}
    filters = {"filters": {"description": "List of filter objects with keys. When making multiple similar queries, e.g., for each ..., use the 'in' operator to group them and provide 'val' as a list.", "use": {"col": "column name (must be valid)", "op": "operator: ==, !=, >, <, >=, <=, in, not in, is null, is not null", "val": "filter value"}}}
    metrics = {"metrics": {"description": "Use this when the question asks for how many or to find the value of something, otherwise it should be []", "use": {"label": "output column name", "expressionType": "SQL", "sqlExpression": "e.g. \"COUNT(*)\""}}}
    groupby = {"groupby": {"description": "List of columns to group the query by. Should be either valid column or metrics label, otherwise []"}}
    orderby = {"orderby": {"description": "List of [column_name or metric_label, is_ascending_boolean]. Should be either valid column or metrics label, otherwise []"}}
    row_limit = {"row_limit":{"description": "integer, 0 < int <= 30"}}
    endpointDocumention = defaultdict(list)
    with open(updatedToolDocs, "w") as f:
        for endpoint in endpoints.keys():
            description = getDescription(endpoint)
            columnTables = getTables(endpoints[endpoint])
            columns = {"columns": {"description": "list of columns to select. Use only these valid columns. Don't use extra columns, only the ones you need. If using metrics, all columns must appear in groupby.", "Valid Columns": columnTables}}
            endpointDocumention[endpoint].append({"description": description})
            endpointDocumention[endpoint].append(args)
            endpointDocumention[endpoint].append(columns)
            endpointDocumention[endpoint].append(filters)
            endpointDocumention[endpoint].append(metrics)
            endpointDocumention[endpoint].append(groupby)
            endpointDocumention[endpoint].append(orderby)
            endpointDocumention[endpoint].append(row_limit)
        json.dump(endpointDocumention, fp=f, indent=2)


if __name__ == "__main__":
    writeUpdateToolDocs()