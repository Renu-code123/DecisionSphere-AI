from typing import Dict, Any
import datetime
from app.agents.base import BaseAgent
from app.mcp import tools

class DataCollectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DataCollectionAgent",
            instructions="You gather real-time weather, air quality, and traffic data using municipal tool APIs."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Determine location/community name. For this demo, let's query base regions based on ID
        comm_id = state.get("community_id", 1)
        location = "Zone A (Coastal)" if comm_id == 1 else "Zone C (River Valley)"
        if comm_id == 2:
            location = "Zone B (Industrial)"
            
        weather = tools.get_weather(location)
        aqi = tools.get_air_quality(location)
        traffic = tools.get_traffic("Highway 101" if comm_id == 1 else "Main St")
        coords = tools.get_coordinates(location)
        
        state["raw_data"] = {
            "location": location,
            "weather": weather,
            "air_quality": aqi,
            "traffic": traffic,
            "coordinates": coords,
            "population": 15000 if comm_id == 1 else (8000 if comm_id == 2 else 12000)
        }
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Query real-time APIs",
            "result_summary": f"Fetched weather ({weather['summary']}), AQI ({aqi['aqi']}), and traffic info for {location}.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "Data collection fallback complete."
