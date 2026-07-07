import os
import csv
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Optional
from app.rag.vector_store import vector_store
from app.db import engine

# --- Helper to connect to SQLite directly for SQL Query Tool ---
def get_raw_connection():
    # Extracts the sqlite file from sqlite:///./decisionsphere.db -> ./decisionsphere.db
    db_url = engine.url
    if db_url.drivername == "sqlite":
        return sqlite3.connect(db_url.database or "./decisionsphere.db")
    raise ValueError("Direct SQL query tool currently only supports SQLite in this version.")

# 1. Weather Tool
def get_weather(location: str) -> Dict[str, Any]:
    """Get current weather forecast for a location/community."""
    loc_lower = location.lower()
    if "coastal" in loc_lower or "zone a" in loc_lower:
        return {"temp": 28.5, "humidity": 82, "rainfall_24h_mm": 115.0, "wind_speed_kmh": 22, "summary": "Heavy Rain & Storm Warning"}
    elif "river" in loc_lower or "zone c" in loc_lower:
        return {"temp": 22.0, "humidity": 75, "rainfall_24h_mm": 65.0, "wind_speed_kmh": 12, "summary": "Continuous Drizzle"}
    else:
        return {"temp": 25.0, "humidity": 55, "rainfall_24h_mm": 5.0, "wind_speed_kmh": 8, "summary": "Partly Cloudy"}

# 2. Air Quality Tool
def get_air_quality(location: str) -> Dict[str, Any]:
    """Get current air quality index (AQI) for a location."""
    loc_lower = location.lower()
    if "industrial" in loc_lower or "zone b" in loc_lower:
        return {"aqi": 185, "main_pollutant": "PM2.5", "status": "Unhealthy", "recommendation": "Wear masks, reduce outdoor activity."}
    else:
        return {"aqi": 42, "main_pollutant": "O3", "status": "Good", "recommendation": "Air quality is ideal."}

# 3. Traffic Tool
def get_traffic(location: str) -> Dict[str, Any]:
    """Get traffic congestion levels and incidents for a location."""
    loc_lower = location.lower()
    if "highway" in loc_lower or "main st" in loc_lower:
        return {"congestion_pct": 85, "delay_minutes": 25, "active_incidents": ["Minor Accident at Lane 3", "Construction blockage"], "status": "Severe"}
    else:
        return {"congestion_pct": 18, "delay_minutes": 0, "active_incidents": [], "status": "Fluid"}

# 4. Maps Tool
def get_coordinates(location: str) -> Dict[str, Any]:
    """Get spatial coordinates (lat/lng) for a community boundary."""
    loc_lower = location.lower()
    if "zone a" in loc_lower or "coastal" in loc_lower:
        return {"lat": 34.0522, "lng": -118.2437, "bounds": "Polygon((-118.25, 34.04), (-118.24, 34.04), (-118.24, 34.06))"}
    elif "zone c" in loc_lower or "river" in loc_lower:
        return {"lat": 34.0822, "lng": -118.2737, "bounds": "Polygon((-118.28, 34.07), (-118.27, 34.07), (-118.27, 34.09))"}
    else:
        return {"lat": 34.0622, "lng": -118.2537, "bounds": "Polygon((-118.26, 34.05), (-118.25, 34.05), (-118.25, 34.07))"}

# 5. Hospital Finder
def find_hospitals(location: str) -> List[Dict[str, Any]]:
    """Find hospitals and medical centers nearest to a location."""
    return [
        {"name": "DecisionSphere Memorial Hospital", "address": "100 Wellness Way", "distance_km": 1.2, "emergency_beds_available": 14, "phone": "555-0199"},
        {"name": "St. Jude Community Clinic", "address": "404 Recovery Blvd", "distance_km": 3.5, "emergency_beds_available": 3, "phone": "555-0182"}
    ]

# 6. Police Finder
def find_police_stations(location: str) -> List[Dict[str, Any]]:
    """Find police stations and safety responder hubs near a location."""
    return [
        {"name": "Metro Precinct Station", "address": "500 Justice Ave", "distance_km": 2.1, "active_patrols": 8, "phone": "555-0911"},
        {"name": "Northside Patrol Outpost", "address": "12 Safety Rd", "distance_km": 4.8, "active_patrols": 2, "phone": "555-0912"}
    ]

# 7. News Tool
def search_safety_news(query: str) -> List[Dict[str, Any]]:
    """Retrieve recent news articles relating to community safety or disasters."""
    return [
        {"title": "Local Council Warns of Flood Risk", "source": "City Herald", "date": "Today", "snippet": "With rain forecasted to reach 100mm, the City Council has placed emergency teams on high alert in coastal Zone A."},
        {"title": "Industrial Zone Air Quality Plummets", "source": "EcoMonitor", "date": "Yesterday", "snippet": "PM2.5 levels surged to 185 due to low wind speeds and increased factory activity."}
    ]

# 8. Government Data Tool
def get_gov_data(registry_code: str) -> Dict[str, Any]:
    """Query government public data registry records."""
    return {
        "registry_code": registry_code,
        "valid_until": "2027-12-31",
        "last_updated": "2026-03-15",
        "record_type": "Municipal Demographic & Infrastructure Survey",
        "details": {"drainage_upgrade_year": 2021, "power_grid_capacity_mw": 150, "evacuation_routes_active": True}
    }

# 9. Disaster Dataset Tool
def get_disaster_history(location: str) -> List[Dict[str, Any]]:
    """Find historical disaster records for a region."""
    return [
        {"year": 2023, "event": "Flash Flood", "rainfall_mm": 120, "impact": "High. Zone A flooded. 200 citizens evacuated. Schools closed for 2 days."},
        {"year": 2020, "event": "Storm Surge", "rainfall_mm": 95, "impact": "Moderate. Coastal roads blocked. Coastal flooding in Zone A."}
    ]

# 10. Emergency Contacts Tool
def get_emergency_contacts() -> Dict[str, str]:
    """Retrieve high-priority emergency response contact directory."""
    return {
        "Emergency Hotline": "911",
        "Disaster Evacuation Coord": "555-EVAC (3822)",
        "Municipal Flood Response": "555-FLOW (3569)",
        "Air Quality Health Line": "555-SAFE (7233)",
        "Community Shelters Info": "555-ROOM (7666)",
        "Police Admin": "555-0100"
    }

# 11. PDF Reader
def read_pdf(file_path: str) -> str:
    """Read and extract raw text from an uploaded PDF file."""
    if not os.path.exists(file_path):
        return f"Error: PDF File {file_path} not found."
    try:
        # For simplicity and robust parsing without strict external binary dependancies on Windows,
        # we will check if it's text-like or read it with a fallback.
        # Real PDF parsing can use a simple package, but we handle it gracefully here.
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)
        return f"[PDF Extract from {os.path.basename(file_path)}]\n{content}"
    except Exception as e:
        return f"Error reading PDF: {e}"

# 12. CSV Reader
def read_csv(file_path: str) -> List[List[str]]:
    """Read rows and columns from an uploaded CSV file."""
    if not os.path.exists(file_path):
        return [["Error", f"CSV File {file_path} not found."]]
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return [row for row in reader][:100] # Return first 100 rows for brevity
    except Exception as e:
        return [["Error", str(e)]]

# 13. Excel Reader
def read_excel(file_path: str) -> Dict[str, Any]:
    """Read sheets and data tables from an Excel file."""
    if not os.path.exists(file_path):
        return {"error": f"Excel File {file_path} not found."}
    try:
        # Use pandas to read Excel
        df = pd.read_excel(file_path)
        # Convert first 50 rows to dict
        return {
            "sheet_name": "Sheet1",
            "columns": list(df.columns),
            "rows": df.head(50).to_dict(orient="records")
        }
    except Exception as e:
        # Return fallback mock if pandas Excel engine fails
        return {"error": f"Failed to read Excel: {e}. Ensure 'openpyxl' is installed."}

# 14. SQL Query Tool
def run_sql_query(query: str) -> List[Dict[str, Any]]:
    """Execute read-only SQL queries on the database for analysis."""
    # Safety Check: Disallow modifying statements to prevent SQL Injection damage
    q_lower = query.lower().strip()
    if not q_lower.startswith("select"):
        return [{"error": "Only SELECT queries are allowed for safety reasons."}]
        
    try:
        conn = get_raw_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        return [{"error": f"SQL Execution error: {e}"}]

# 15. Vector Search Tool
def search_vector_store(query: str) -> List[Dict[str, Any]]:
    """Query the local document vector database for policies, procedures, and manuals."""
    return vector_store.similarity_search(query, k=3)

# 16. File Search Tool
def search_files(directory: str, query: str) -> List[Dict[str, Any]]:
    """Search for code or logs in the project workspace."""
    results = []
    if not os.path.exists(directory):
        return [{"error": f"Directory {directory} not found."}]
        
    for root, dirs, files in os.walk(directory):
        # Exclude node_modules, .git, venv
        if any(x in root for x in ["node_modules", ".git", "venv", "__pycache__", "weights"]):
            continue
        for file in files:
            if file.endswith((".py", ".txt", ".json", ".md", ".css", ".ts", ".tsx")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                results.append({
                                    "file": os.path.relpath(path, directory),
                                    "line": line_no,
                                    "content": line.strip()
                                })
                                if len(results) >= 20: # Cap results for performance
                                    return results
                except Exception:
                    pass
    return results
