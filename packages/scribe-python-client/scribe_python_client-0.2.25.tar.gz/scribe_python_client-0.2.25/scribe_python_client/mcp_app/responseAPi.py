from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import json

readPath = Path(__file__).parent / "toolsDescriptions/tool_docs.json"
load_dotenv()

def main(): 
    client = OpenAI()

    with open(readPath, "r") as f:
        tool_description = json.load(f)
    instructions = "Tool usage guidance:\n" + json.dumps(tool_description, indent=2)


    response = client.responses.create(
        model= "gpt-4o",
        tools= [{
                "type": "mcp",
                "server_label": "ScribeMCP",
                "server_url": "https://eporath-scribe-mcp.hf.space/mcp",
                "require_approval": "never",
            }],
        input = "Query the vulnerabilities table for the top 5 risky CVEs - KEV vulnerabilities and vulnerabilities with highest EPSS scores." +
        "Take each query from the and Query the vulnerabilities table of to get the list of affected products."
        #instructions = instructions
    )
    print(response.output_text)


if __name__ == "__main__":
    main()