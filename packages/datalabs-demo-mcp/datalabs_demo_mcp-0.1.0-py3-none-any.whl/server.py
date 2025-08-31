from mcp.server.fastmcp import FastMCP
import pandas as pd

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Read CSV
@mcp.tool()
def read_csv(file_path: str) -> pd.DataFrame:
    """Read a CSV file and return a DataFrame"""
    df = pd.DataFrame(
        data={"col1": [1, 2, 3, 4, 5], "col2": [3, 4, 5, 6, 7]}
    )  # Dummy data for example
    return df


if __name__ == "__main__":
    mcp.run()
