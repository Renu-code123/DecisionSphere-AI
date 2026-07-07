import os
import joblib
import pandas as pd
from app.ml.train import WEIGHTS_DIR, train_all

class MLPredictor:
    def __init__(self):
        # Trigger training if models do not exist
        if not os.path.exists(WEIGHTS_DIR) or not os.path.exists(os.path.join(WEIGHTS_DIR, "flood_model.joblib")):
            print("Model weights not found. Training models on synthetic data first...")
            train_all()
            
        self.flood_model = joblib.load(os.path.join(WEIGHTS_DIR, "flood_model.joblib"))
        self.traffic_model = joblib.load(os.path.join(WEIGHTS_DIR, "traffic_model.joblib"))
        self.air_quality_model = joblib.load(os.path.join(WEIGHTS_DIR, "air_quality_model.joblib"))
        self.disease_model = joblib.load(os.path.join(WEIGHTS_DIR, "disease_model.joblib"))
        self.crime_model = joblib.load(os.path.join(WEIGHTS_DIR, "crime_model.joblib"))
        self.water_model = joblib.load(os.path.join(WEIGHTS_DIR, "water_model.joblib"))
        self.energy_model = joblib.load(os.path.join(WEIGHTS_DIR, "energy_model.joblib"))

    def predict_flood(self, elevation: float, rainfall: float, soil_moisture: float, distance_to_water: float, drainage: float) -> tuple[float, float]:
        df = pd.DataFrame([{
            'elevation': elevation,
            'rainfall': rainfall,
            'soil_moisture': soil_moisture,
            'distance_to_water': distance_to_water,
            'drainage': drainage
        }])
        pred = self.flood_model.predict(df)[0]
        # Predict probability
        prob = self.flood_model.predict_proba(df)[0][1]
        return float(pred), float(prob)

    def predict_traffic(self, hour: int, day: int, rain: float, construction: int, accident: int, base_volume: float) -> float:
        df = pd.DataFrame([{
            'hour': hour,
            'day': day,
            'rain': rain,
            'construction': construction,
            'accident': accident,
            'base_volume': base_volume
        }])
        pred = self.traffic_model.predict(df)[0]
        return float(pred)

    def predict_air_quality(self, industrial: float, vehicles: float, temp: float, wind: float, humidity: float) -> float:
        df = pd.DataFrame([{
            'industrial': industrial,
            'vehicles': vehicles,
            'temp': temp,
            'wind': wind,
            'humidity': humidity
        }])
        pred = self.air_quality_model.predict(df)[0]
        return float(pred)

    def predict_disease(self, pop_density: float, temp: float, humidity: float, active_cases: int, vax_rate: float) -> float:
        df = pd.DataFrame([{
            'pop_density': pop_density,
            'temp': temp,
            'humidity': humidity,
            'active_cases': active_cases,
            'vax_rate': vax_rate
        }])
        pred = self.disease_model.predict(df)[0]
        return float(pred)

    def predict_crime(self, unemployment: float, patrol: float, lighting: float, time_of_day: float, area_type: int) -> float:
        df = pd.DataFrame([{
            'unemployment': unemployment,
            'patrol': patrol,
            'lighting': lighting,
            'time_of_day': time_of_day,
            'area_type': area_type
        }])
        pred = self.crime_model.predict(df)[0]
        return float(pred)

    def predict_water(self, population: float, temp: float, day: int, industrial: float, restrictions: int) -> float:
        df = pd.DataFrame([{
            'population': population,
            'temp': temp,
            'day': day,
            'industrial': industrial,
            'restrictions': restrictions
        }])
        pred = self.water_model.predict(df)[0]
        return float(pred)

    def predict_energy(self, population: float, temp: float, humidity: float, commercial: float, solar: float) -> float:
        df = pd.DataFrame([{
            'population': population,
            'temp': temp,
            'humidity': humidity,
            'commercial': commercial,
            'solar': solar
        }])
        pred = self.energy_model.predict(df)[0]
        return float(pred)

# Global singleton predictor instance
ml_predictor = MLPredictor()
