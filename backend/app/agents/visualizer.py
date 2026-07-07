from typing import Dict, Any
import datetime
import random
from app.agents.base import BaseAgent

class VisualizationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="VisualizationAgent",
            instructions="You structure metrics into JSON formats optimized for charts, maps, and gauges."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        comm_id = state.get("community_id", 1)
        raw = state.get("raw_data", {})
        predictions = state.get("predictions", {})
        
        # --- Generate Mock Spatial Markers for InteractiveMap.tsx ---
        # Center coordinates
        lat = raw.get("coordinates", {}).get("lat", 34.06)
        lng = raw.get("coordinates", {}).get("lng", -118.25)
        
        markers = [
            {"id": "hosp_1", "type": "hospital", "label": "DecisionSphere Memorial Hospital", "lat": lat + 0.005, "lng": lng - 0.003, "status": "active"},
            {"id": "police_1", "type": "police", "label": "Metro Precinct Station", "lat": lat - 0.002, "lng": lng + 0.004, "status": "active"},
            {"id": "shelter_1", "type": "shelter", "label": "Municipal Shelter Hub", "lat": lat + 0.008, "lng": lng + 0.008, "status": "open" if predictions.get("flood_probability", 0) > 0.6 else "standby"}
        ]
        
        # Add risk zone marker
        if predictions.get("flood_probability", 0) > 0.6:
            markers.append({"id": "risk_zone", "type": "flood_zone", "label": "Zone A High-Risk Flooding Sector", "lat": lat + 0.002, "lng": lng - 0.001, "radius": 400})
        elif raw.get("air_quality", {}).get("aqi", 0) > 120:
            markers.append({"id": "pollution_zone", "type": "pollution_zone", "label": "Industrial AQI Hotspot", "lat": lat + 0.003, "lng": lng - 0.005, "radius": 600})
            
        # --- Generate Historical Resource Data for AnalyticsChart.tsx ---
        # Last 7 days consumption trends
        base_water = predictions.get("water_consumption", 15.0)
        base_energy = predictions.get("energy_usage", 30.0)
        
        weekly_trends = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for idx, day in enumerate(days):
            # Add some fluctuation
            f_water = base_water + random.uniform(-2, 2)
            f_energy = base_energy + random.uniform(-4, 4)
            # Add temperature effect
            temp_effect = 1.05 if idx in [4, 5] else 1.0
            weekly_trends.append({
                "day": day,
                "water": round(max(1.0, f_water * temp_effect), 1),
                "energy": round(max(1.0, f_energy * temp_effect), 1),
                "aqi": int(raw.get("air_quality", {}).get("aqi", 50) + random.uniform(-10, 10))
            })
            
        visualization_data = {
            "markers": markers,
            "weekly_trends": weekly_trends,
            "risk_distribution": [
                {"name": "Flood Risk", "value": int(predictions.get("flood_probability", 0) * 100)},
                {"name": "Traffic", "value": int(predictions.get("traffic_congestion", 20))},
                {"name": "Air Pollution", "value": int((predictions.get("air_quality", 50)/300) * 100)},
                {"name": "Disease", "value": int(predictions.get("disease_spread", 1) * 10)},
                {"name": "Crime", "value": int(predictions.get("crime_risk", 3) * 10)}
            ]
        }
        
        state["visualization"] = visualization_data
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Assemble chart and spatial JSON models",
            "result_summary": f"Built structural coordinate arrays ({len(markers)} nodes) and weekly trend history arrays.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "Visualization models ready."
