import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_DIR = os.path.join(MODEL_DIR, "weights")

def ensure_dirs():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)

def train_flood_model():
    print("Training Flood Prediction Model...")
    # Target: binary classification (1 = flood risk, 0 = safe)
    # Features: [elevation, rainfall_mm, soil_moisture_pct, distance_to_water_m, drainage_capacity_pct]
    np.random.seed(42)
    n_samples = 1000
    
    elevation = np.random.uniform(5, 100, n_samples)
    rainfall = np.random.uniform(0, 150, n_samples)
    soil_moisture = np.random.uniform(10, 95, n_samples)
    distance_to_water = np.random.uniform(10, 2000, n_samples)
    drainage = np.random.uniform(20, 100, n_samples)
    
    # Simple logic for flood probability
    prob = (rainfall * 0.4 + soil_moisture * 0.3 - elevation * 0.2 - distance_to_water * 0.1 - drainage * 0.2)
    # Normalize to 0-1
    prob = (prob - prob.min()) / (prob.max() - prob.min())
    y = (prob > 0.6).astype(int)
    
    X = pd.DataFrame({
        'elevation': elevation,
        'rainfall': rainfall,
        'soil_moisture': soil_moisture,
        'distance_to_water': distance_to_water,
        'drainage': drainage
    })
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "flood_model.joblib"))
    print("Flood model saved.")

def train_traffic_model():
    print("Training Traffic Congestion Model...")
    # Target: continuous rating (0 to 100)
    # Features: [hour_of_day, day_of_week, rain_intensity, construction_active, accident_reported, base_volume]
    np.random.seed(42)
    n_samples = 1000
    
    hour = np.random.randint(0, 24, n_samples)
    day = np.random.randint(0, 7, n_samples)
    rain = np.random.uniform(0, 50, n_samples)
    construction = np.random.randint(0, 2, n_samples)
    accident = np.random.randint(0, 2, n_samples)
    base_volume = np.random.uniform(100, 1000, n_samples)
    
    # Calculate congestion
    rush_hour = np.isin(hour, [7, 8, 9, 16, 17, 18]).astype(int)
    congestion = (rush_hour * 40 + rain * 0.4 + construction * 15 + accident * 25 + (base_volume/10) * 0.2)
    congestion = np.clip(congestion, 5, 100)
    
    X = pd.DataFrame({
        'hour': hour,
        'day': day,
        'rain': rain,
        'construction': construction,
        'accident': accident,
        'base_volume': base_volume
    })
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, congestion)
    
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "traffic_model.joblib"))
    print("Traffic model saved.")

def train_air_quality_model():
    print("Training Air Quality Model...")
    # Target: AQI value (0 to 300+)
    # Features: [industrial_output_pct, vehicle_density, temperature, wind_speed, humidity]
    np.random.seed(42)
    n_samples = 1000
    
    industrial = np.random.uniform(10, 100, n_samples)
    vehicles = np.random.uniform(50, 500, n_samples)
    temp = np.random.uniform(0, 40, n_samples)
    wind = np.random.uniform(0, 25, n_samples)
    humidity = np.random.uniform(10, 95, n_samples)
    
    aqi = (industrial * 0.8 + vehicles * 0.3 + temp * 0.1 - wind * 1.5 + humidity * 0.05)
    aqi = np.clip(aqi, 10, 350)
    
    X = pd.DataFrame({
        'industrial': industrial,
        'vehicles': vehicles,
        'temp': temp,
        'wind': wind,
        'humidity': humidity
    })
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, aqi)
    
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "air_quality_model.joblib"))
    print("Air quality model saved.")

def train_disease_model():
    print("Training Disease Spread Model...")
    # Target: disease spread score (0.0 to 10.0)
    # Features: [population_density, temperature, humidity, active_cases, vaccination_rate_pct]
    np.random.seed(42)
    n_samples = 1000
    
    pop_density = np.random.uniform(100, 15000, n_samples)
    temp = np.random.uniform(10, 35, n_samples)
    humidity = np.random.uniform(20, 90, n_samples)
    active_cases = np.random.randint(0, 500, n_samples)
    vax_rate = np.random.uniform(30, 95, n_samples)
    
    spread = (pop_density/1500 + temp*0.05 + humidity*0.02 + active_cases*0.01 - vax_rate*0.05)
    spread = np.clip(spread, 0.1, 10.0)
    
    X = pd.DataFrame({
        'pop_density': pop_density,
        'temp': temp,
        'humidity': humidity,
        'active_cases': active_cases,
        'vax_rate': vax_rate
    })
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, spread)
    
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "disease_model.joblib"))
    print("Disease model saved.")

def train_crime_model():
    print("Training Crime Risk Model...")
    # Target: crime risk score (0.0 to 10.0)
    # Features: [unemployment_rate_pct, police_patrol_freq, lighting_quality_pct, time_of_day, area_type_code]
    np.random.seed(42)
    n_samples = 1000
    
    unemployment = np.random.uniform(2, 20, n_samples)
    patrol = np.random.uniform(1, 10, n_samples)
    lighting = np.random.uniform(10, 100, n_samples)
    time_of_day = np.random.uniform(0, 24, n_samples)
    area_type = np.random.randint(0, 3, n_samples) # 0: residential, 1: commercial, 2: industrial
    
    # Higher risk at night (time 20-4), higher unemployment, lower patrol, lower lighting
    night = ((time_of_day > 20) | (time_of_day < 4)).astype(int)
    risk = (unemployment * 0.3 - patrol * 0.4 - lighting * 0.05 + night * 2.5 + area_type * 0.5)
    risk = np.clip(risk, 0.1, 10.0)
    
    X = pd.DataFrame({
        'unemployment': unemployment,
        'patrol': patrol,
        'lighting': lighting,
        'time_of_day': time_of_day,
        'area_type': area_type
    })
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, risk)
    
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "crime_model.joblib"))
    print("Crime model saved.")

def train_water_model():
    print("Training Water Consumption Model...")
    # Target: MegaLitres per day
    # Features: [population, temperature, day_of_week, industrial_use_pct, water_restrictions_level]
    np.random.seed(42)
    n_samples = 1000
    
    pop = np.random.uniform(1000, 50000, n_samples)
    temp = np.random.uniform(10, 42, n_samples)
    day = np.random.randint(0, 7, n_samples)
    industrial = np.random.uniform(5, 50, n_samples)
    restrictions = np.random.randint(0, 4, n_samples)
    
    water = (pop * 0.0003 + temp * 0.1 + industrial * 0.05 - restrictions * 1.5)
    water = np.clip(water, 0.5, 30.0)
    
    X = pd.DataFrame({
        'population': pop,
        'temp': temp,
        'day': day,
        'industrial': industrial,
        'restrictions': restrictions
    })
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, water)
    
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "water_model.joblib"))
    print("Water consumption model saved.")

def train_energy_model():
    print("Training Energy Usage Model...")
    # Target: MegaWatt hours per day
    # Features: [population, temperature, humidity, commercial_activity_pct, solar_generation_mw]
    np.random.seed(42)
    n_samples = 1000
    
    pop = np.random.uniform(1000, 50000, n_samples)
    temp = np.random.uniform(10, 42, n_samples)
    humidity = np.random.uniform(10, 95, n_samples)
    commercial = np.random.uniform(10, 90, n_samples)
    solar = np.random.uniform(0, 50, n_samples)
    
    # AC usage triggers at temp > 28, heating at temp < 15
    ac_heating = np.maximum(0, temp - 28) * 1.2 + np.maximum(0, 15 - temp) * 0.8
    energy = (pop * 0.0005 + ac_heating + commercial * 0.2 - solar * 0.3)
    energy = np.clip(energy, 1.0, 50.0)
    
    X = pd.DataFrame({
        'population': pop,
        'temp': temp,
        'humidity': humidity,
        'commercial': commercial,
        'solar': solar
    })
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, energy)
    
    joblib.dump(model, os.path.join(WEIGHTS_DIR, "energy_model.joblib"))
    print("Energy usage model saved.")

def train_all():
    ensure_dirs()
    train_flood_model()
    train_traffic_model()
    train_air_quality_model()
    train_disease_model()
    train_crime_model()
    train_water_model()
    train_energy_model()
    print("All ML models trained successfully.")

if __name__ == "__main__":
    train_all()
