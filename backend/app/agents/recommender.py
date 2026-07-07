from typing import Dict, Any
import datetime
from app.agents.base import BaseAgent

class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RecommendationAgent",
            instructions="You generate actionable recommendations for citizens, governments, and emergency responders."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query", "")
        raw = state.get("raw_data", {})
        analysis = state.get("analysis", {})
        predictions = state.get("predictions", {})
        memory = state.get("memory_context", "")
        
        prompt = f"""
        User Query: {query}
        Location: {raw.get('location')}
        Current Weather: {raw.get('weather', {}).get('summary')} (Rain: {raw.get('weather', {}).get('rainfall_24h_mm')}mm)
        Air Quality: {raw.get('air_quality', {}).get('status')} (AQI: {raw.get('air_quality', {}).get('aqi')})
        Calculated Risk: {analysis.get('risk_score')}/10
        Health Index: {analysis.get('health_index')}/100
        Active Anomalies: {analysis.get('anomalies')}
        Guidelines retrieved from memory:
        {memory}
        
        Based on this state, generate 4-5 bullet points of actionable recommendations.
        Separate recommendations by audience:
        - Citizens (e.g. safety measures, travel plans)
        - Government (e.g. school closures, traffic routing, industrial regulations)
        - Emergency Responders (e.g. deployment locations, warning systems)
        """
        
        recs_text = self.run_llm(prompt)
        
        # Split text into bullet points for clean frontend rendering
        lines = recs_text.split("\n")
        recommendations = [line.strip().lstrip("-* ").strip() for line in lines if line.strip() and (line.strip().startswith("-") or line.strip().startswith("*") or any(keyword in line.lower() for keyword in ["citizen", "government", "emergency"]))]
        
        # If split is empty or raw, just use lines
        if not recommendations:
            recommendations = [line.strip() for line in lines if line.strip()]
            
        state["recommendations"] = recommendations
        state["raw_recommendations_text"] = recs_text
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Generate actionable advice",
            "result_summary": f"Created custom recommendations addressing: citizens, administration, and response teams.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return (
            "- Citizens: Avoid low-lying river paths; delay non-essential travel in Zone A.\n"
            "- Government: Coordinate with school boards regarding closure due to heavy rainfall.\n"
            "- Responders: Pre-position flood barrier units along Zone A coastal drainage channels."
        )
