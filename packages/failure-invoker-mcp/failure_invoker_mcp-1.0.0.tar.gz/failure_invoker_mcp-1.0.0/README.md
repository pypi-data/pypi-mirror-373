# Failure Invoker MCP Server

Invoke mock AZ, DB, and MSK Failure with AWS FIS, AWS SSM.

## Usage

### *.json file

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "uvx",
      "args": ["failure-invoker-mcp@latest"],
      "env": {
        "AWS_ACCESS_KEY": "",
        "AWS_SECRET_ID": ""
      }
    }
  }
}
```

### Strands Agent SDK

```python
failure_invoker_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["failure-invoker-mcp@latest"],
            env={
              "AWS_ACCESS_KEY": "",
              "AWS_SECRET_ID": "",
            },
        )
    )
)

failure_invoker_client.start()

agent = Agent(
    model,
    system_prompt,
    tools=[failure_invoker_client.list_tools_sync()],
)
```
