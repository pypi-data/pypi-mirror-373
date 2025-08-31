from dotenv import load_dotenv
from pydantic import BaseModel
import json
import requests
from pathlib import Path

path1 = Path(__file__).parent / "query.json"

class QueryString(BaseModel):
    query: dict
    title: str = ""

def test_queries(payload):
    url = f"http://127.0.0.1:8000/vulnerabilities"       
    response = requests.post(url, json=payload)
    print("Status code:", response.status_code)
    try:
        response_json = response.json()
        print("Response JSON:", response_json)
    except Exception as e:
        print("Failed to parse JSON:", str(e))
    
if __name__ == "__main__":
    
    with open(path1, "r") as f:
        data = json.load(f)
    print(data)
    test_queries(payload=data)


#json.loads(query.querystr)

    
    #print(type(input["querystr"]))
    #print(type(json.dumps(queries2["querystr"])))

    #test = json.dumps(input["item"])
    #print(type(test))
    