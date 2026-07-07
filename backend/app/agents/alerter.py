from typing import Dict, Any
import datetime
from app.agents.base import BaseAgent

class AlertAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AlertAgent",
            instructions="You evaluate metrics against warning thresholds to dispatch emergency alerts."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        predictions = state.get("predictions", {})
        raw = state.get("raw_data", {})
        comm_id = state.get("community_id", 1)
        
        alerts = []
        
        # Check Flood risk
        flood_prob = predictions.get("flood_probability", 0.0)
        if flood_prob > 0.7:
            alerts.append({
                "community_id": comm_id,
                "severity": "danger",
                "category": "disaster",
                "message": "CRITICAL flood hazard imminent! Evacuate low-lying coastal paths in Zone A immediately."
            })
        elif flood_prob > 0.4:
            alerts.append({
                "community_id": comm_id,
                "severity": "warning",
                "category": "weather",
                "message": "Elevated water logging risk. Pre-position drainage pumps and drive with caution."
            })
            
        # Check Air Quality
        aqi = raw.get("air_quality", {}).get("aqi", 50)
        if aqi > 180:
            alerts.append({
                "community_id": comm_id,
                "severity": "danger",
                "category": "health",
                "message": "AIR QUALITY EMERGENCY: AQI is dangerously high. Sensitive groups should remain indoors."
            })
        elif aqi > 100:
            alerts.append({
                "community_id": comm_id,
                "severity": "warning",
                "category": "health",
                "message": "Moderate air pollution warning. Use protective masks in heavy industrial hubs."
            })
            
        # Check Traffic congestion
        traffic = predictions.get("traffic_congestion", 0.0)
        if traffic > 80:
            alerts.append({
                "community_id": comm_id,
                "severity": "warning",
                "category": "traffic",
                "message": "Severe gridlock predicted on main highway arterials. Divert routes."
            })
            
        state["alerts_triggered"] = alerts
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Threshold safety check",
            "result_summary": f"Triggered {len(alerts)} alerts based on current predictions.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "Alert dispatch fallback complete."
