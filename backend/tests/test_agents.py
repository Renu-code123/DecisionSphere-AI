from app.agents.coordinator import CoordinatorAgent
from app.agents.memory import MemoryAgent
from app.agents.collector import DataCollectionAgent
from app.agents.analyst import AnalysisAgent

def test_memory_agent():
    agent = MemoryAgent()
    state = {"query": "Should schools close?", "steps": []}
    res = agent.execute(state)
    assert "memory_context" in res
    assert len(res["steps"]) == 1

def test_data_collection_agent():
    agent = DataCollectionAgent()
    state = {"community_id": 1, "steps": []}
    res = agent.execute(state)
    assert "raw_data" in res
    assert res["raw_data"]["location"] == "Zone A (Coastal)"

def test_analyst_agent():
    agent = AnalysisAgent()
    state = {
        "raw_data": {
            "location": "Zone A",
            "weather": {"rainfall_24h_mm": 120.0},
            "air_quality": {"aqi": 50},
            "traffic": {"congestion_pct": 20}
        },
        "predictions": {
            "flood_probability": 0.85
        },
        "steps": []
    }
    res = agent.execute(state)
    assert "analysis" in res
    assert res["analysis"]["health_index"] < 80 # check logic deduction works
    assert len(res["analysis"]["anomalies"]) > 0

def test_coordinator_agent():
    # Force mock mode by running with offline inputs
    agent = CoordinatorAgent()
    state = {
        "query": "Should schools close?",
        "community_id": 1,
        "steps": []
    }
    res = agent.execute(state)
    assert "response" in res
    assert len(res["steps"]) > 2
