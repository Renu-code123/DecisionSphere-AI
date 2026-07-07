from typing import Dict, Any
import datetime
from app.agents.base import BaseAgent
from app.ml.models import ml_predictor

class PredictionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PredictionAgent",
            instructions="You analyze raw metrics and run machine learning models, then explain their outputs."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        raw = state.get("raw_data", {})
        weather = raw.get("weather", {})
        aqi = raw.get("air_quality", {})
        traffic = raw.get("traffic", {})
        population = raw.get("population", 10000)
        
        # --- Extract features ---
        temp = weather.get("temp", 25.0)
        humidity = weather.get("humidity", 50.0)
        rain = weather.get("rainfall_24h_mm", 0.0)
        
        # --- Run ML predictions ---
        # Elevation: Zone A is low-lying (15m), Zone C is higher (40m)
        elevation = 15.0 if "Zone A" in raw.get("location", "") else 40.0
        flood_pred, flood_prob = ml_predictor.predict_flood(
            elevation=elevation,
            rainfall=rain,
            soil_moisture=humidity, # use humidity as proxy for soil moisture
            distance_to_water=150.0,
            drainage=65.0
        )
        
        traffic_score = ml_predictor.predict_traffic(
            hour=datetime.datetime.now().hour,
            day=datetime.datetime.now().weekday(),
            rain=rain,
            construction=1 if traffic.get("congestion_pct", 0) > 70 else 0,
            accident=1 if len(traffic.get("active_incidents", [])) > 0 else 0,
            base_volume=population / 20.0
        )
        
        aqi_score = ml_predictor.predict_air_quality(
            industrial=80.0 if aqi.get("aqi", 0) > 100 else 30.0,
            vehicles=300.0 if traffic_score > 60 else 120.0,
            temp=temp,
            wind=12.0,
            humidity=humidity
        )
        
        disease_score = ml_predictor.predict_disease(
            pop_density=population / 2.0,
            temp=temp,
            humidity=humidity,
            active_cases=12,
            vax_rate=82.0
        )
        
        crime_score = ml_predictor.predict_crime(
            unemployment=6.5,
            patrol=4.0,
            lighting=75.0,
            time_of_day=21.0,
            area_type=1
        )
        
        water_usage = ml_predictor.predict_water(
            population=population,
            temp=temp,
            day=datetime.datetime.now().weekday(),
            industrial=25.0,
            restrictions=1 if temp > 35.0 else 0
        )
        
        energy_usage = ml_predictor.predict_energy(
            population=population,
            temp=temp,
            humidity=humidity,
            commercial=45.0,
            solar=15.0
        )
        
        predictions_map = {
            "flood_probability": flood_prob,
            "traffic_congestion": traffic_score,
            "air_quality": aqi_score,
            "disease_spread": disease_score,
            "crime_risk": crime_score,
            "water_consumption": water_usage,
            "energy_usage": energy_usage
        }
        
        state["predictions"] = predictions_map
        
        # --- Generate Gemini Explanation ---
        explain_prompt = f"""
        Explain the following community predictions for a region:
        - Flood Probability: {flood_prob:.2f} (based on 24h rainfall of {rain}mm and elevation of {elevation}m)
        - Traffic Congestion Level: {traffic_score:.1f}% (0-100 scale)
        - Air Quality Index (AQI): {aqi_score:.1f}
        - Disease Spread Indicator: {disease_score:.1f}/10
        - Crime Risk Index: {crime_score:.1f}/10
        - Daily Water Consumption: {water_usage:.1f} MegaLitres
        - Daily Energy Consumption: {energy_usage:.1f} MegaWatt-hours
        
        Provide a concise, 2-paragraph summary explaining the key risks and drivers behind these numbers.
        """
        
        explanation = self.run_llm(explain_prompt)
        state["predictions_explanation"] = explanation
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Run ML predictions & explain",
            "result_summary": f"Calculated 7 urban indicators. Flood probability: {flood_prob:.2%}, AQI: {aqi_score:.1f}.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "Predictions show elevated flood risk in low-lying zones due to current rainfall intensities. Resource consumption is steady."
