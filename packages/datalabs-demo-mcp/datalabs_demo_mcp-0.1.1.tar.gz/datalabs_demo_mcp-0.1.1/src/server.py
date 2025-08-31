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
def read_csv(file_path: str) -> dict:
    """Read a CSV file and return data as a dictionary"""
    df = pd.DataFrame(
        data={"col1": [1, 2, 3, 4, 5], "col2": [3, 4, 5, 6, 7]}
    )  # Dummy data for example
    return df.to_dict('records')


def main():
    """Main entry point for the MCP server"""
    print("Starting MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
