import asyncio
import json
from mcp.server.fastmcp import FastMCP
from app.mcp import tools

# Initialize FastMCP Server (compatible with mcp>=1.0.0)
mcp = FastMCP("decisionsphere-mcp")

@mcp.tool()
def get_weather(location: str) -> dict:
    """Get current weather forecast for a location."""
    return tools.get_weather(location)

@mcp.tool()
def get_air_quality(location: str) -> dict:
    """Get current air quality index (AQI) details for a location."""
    return tools.get_air_quality(location)

@mcp.tool()
def get_traffic(location: str) -> dict:
    """Get traffic congestion levels and incidents for a location."""
    return tools.get_traffic(location)

@mcp.tool()
def get_coordinates(location: str) -> dict:
    """Get spatial coordinates (lat/lng) for a community boundary."""
    return tools.get_coordinates(location)

@mcp.tool()
def find_hospitals(location: str) -> list:
    """Find hospitals and medical centers nearest to a location."""
    return tools.find_hospitals(location)

@mcp.tool()
def find_police_stations(location: str) -> list:
    """Find police stations near a location."""
    return tools.find_police_stations(location)

@mcp.tool()
def search_safety_news(query: str) -> list:
    """Retrieve recent news articles relating to community safety or disasters."""
    return tools.search_safety_news(query)

@mcp.tool()
def get_gov_data(registry_code: str) -> dict:
    """Query government public data registry records."""
    return tools.get_gov_data(registry_code)

@mcp.tool()
def get_disaster_history(location: str) -> list:
    """Find historical disaster records for a region."""
    return tools.get_disaster_history(location)

@mcp.tool()
def get_emergency_contacts() -> dict:
    """Retrieve high-priority emergency response contact directory."""
    return tools.get_emergency_contacts()

@mcp.tool()
def read_pdf(file_path: str) -> str:
    """Read and extract raw text from an uploaded PDF file."""
    return tools.read_pdf(file_path)

@mcp.tool()
def read_csv(file_path: str) -> list:
    """Read rows and columns from an uploaded CSV file."""
    return tools.read_csv(file_path)

@mcp.tool()
def read_excel(file_path: str) -> dict:
    """Read sheets and data tables from an Excel file."""
    return tools.read_excel(file_path)

@mcp.tool()
def run_sql_query(query: str) -> list:
    """Execute read-only SQL SELECT queries on the database."""
    return tools.run_sql_query(query)

@mcp.tool()
def search_vector_store(query: str) -> list:
    """Query the local document vector database for policies and manuals."""
    return tools.search_vector_store(query)

@mcp.tool()
def search_files(directory: str, query: str) -> list:
    """Search for code or logs in the project workspace."""
    return tools.search_files(directory, query)

if __name__ == "__main__":
    mcp.run(transport="stdio")
