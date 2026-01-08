import json


def convert_mcp_to_openai(mcp_tools):
    openai_functions = []

    for tool in mcp_tools.get("tools", []):
        openai_function = {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": tool["inputSchema"].get("properties", {}),
                "required": tool["inputSchema"].get("required", []),
            },
        }
        openai_functions.append(openai_function)

    return {"functions": openai_functions}


if __name__ == "__main__":
    # Example MCP response (Listing Tools (Response))
    mcp_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get current weather information for a location",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name or zip code",
                            }
                        },
                        "required": ["location"],
                    },
                }
            ],
            "nextCursor": "next-page-cursor",
        },
    }

    # Convert MCP to OpenAI format
    openai_spec = convert_mcp_to_openai(mcp_response["result"])

    # Print OpenAI function call specification
    print(json.dumps(openai_spec, indent=2))
