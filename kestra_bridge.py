import os
from fastmcp import FastMCP

# Initialize the MCP Server
mcp = FastMCP("KestraBridge")

# This is the "Mailbox" file inside the shared folder
LOG_FILE = "shared/kestra_errors.log"

@mcp.tool()
def read_deployment_logs() -> str:
    """
    Reads the latest deployment error logs from Kestra.
    Use this tool when you need to know why a deployment failed.
    """
    if not os.path.exists(LOG_FILE):
        return "No error logs found in shared/kestra_errors.log. System appears healthy."
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.read()
        return f"LATEST ERROR LOGS:\n{logs}"
    except Exception as e:
        return f"Failed to read logs: {str(e)}"

@mcp.tool()
def clear_error_logs() -> str:
    """
    Clears the error logs after a fix has been applied.
    """
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        return "Logs cleared successfully."
    return "No logs to clear."

if __name__ == "__main__":
    mcp.run()
