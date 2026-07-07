from typing import Dict, Any
import datetime
from app.agents.base import BaseAgent

class AnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AnalysisAgent",
            instructions="You identify trends, risks, anomalies, and calculate community indicators."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raw = state.get("raw_data", {})
        predictions = state.get("predictions", {})
        
        # --- Quantitative Rules for Health/Risk scores ---
        anomalies = []
        
        # Weather anomaly
        rain_24h = raw.get("weather", {}).get("rainfall_24h_mm", 0.0)
        if rain_24h > 100:
            anomalies.append("CRITICAL: Extreme torrential rainfall detected (>100mm).")
        elif rain_24h > 50:
            anomalies.append("WARNING: Heavy rainfall active (>50mm).")
            
        # Air Quality anomaly
        aqi = raw.get("air_quality", {}).get("aqi", 50)
        if aqi > 150:
            anomalies.append("WARNING: Unhealthy air quality index.")
            
        # Traffic anomaly
        congestion = raw.get("traffic", {}).get("congestion_pct", 0)
        if congestion > 80:
            anomalies.append("WARNING: Severe gridlock on primary transit links.")

        # Compute composite Health Index and Risk Score
        # Start health at 100, deduct based on anomalies and risks
        health = 100.0
        if rain_24h > 100: health -= 30
        elif rain_24h > 50: health -= 15
        if aqi > 150: health -= 20
        if congestion > 80: health -= 15
        
        flood_prob = predictions.get("flood_probability", 0.0)
        if flood_prob > 0.7: health -= 20
        elif flood_prob > 0.4: health -= 10
        
        health = max(10.0, health)
        
        # Risk score (0 to 10 scale)
        risk = (flood_prob * 4.0 + (aqi / 350.0) * 3.0 + (congestion / 100.0) * 3.0)
        risk = min(10.0, max(0.0, risk))
        
        analysis_map = {
            "anomalies": anomalies,
            "health_index": round(health, 1),
            "risk_score": round(risk, 1)
        }
        state["analysis"] = analysis_map
        
        # --- Call Gemini to summarize trends ---
        trend_prompt = f"""
        Summarize the current situational trends and vulnerabilities based on:
        - Location: {raw.get('location', 'N/A')}
        - Active Anomalies: {', '.join(anomalies) if anomalies else 'None'}
        - Composite Health Index: {health:.1f}/100
        - Community Risk Score: {risk:.1f}/10
        
        Draft a concise, 1-paragraph brief summarizing the overall risk landscape.
        """
        state["analysis"]["trend_summary"] = self.run_llm(trend_prompt)
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Detect trends & score indexes",
            "result_summary": f"Identified {len(anomalies)} anomalies. Health Index set to {health:.1f}. Risk Score: {risk:.1f}.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "The region shows moderate vulnerabilities due to active weather systems. Recommended to monitor low-lying sectors."
