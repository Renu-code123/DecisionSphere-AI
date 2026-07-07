from app.mcp import tools

def test_weather_tool():
    res = tools.get_weather("Zone A (Coastal)")
    assert "summary" in res
    assert res["rainfall_24h_mm"] > 50

def test_air_quality_tool():
    res = tools.get_air_quality("Zone B")
    assert "aqi" in res
    assert res["aqi"] > 100
    assert res["status"] == "Unhealthy"

def test_traffic_tool():
    res = tools.get_traffic("Highway 101")
    assert "congestion_pct" in res
    assert res["congestion_pct"] > 50
    assert res["status"] == "Severe"

def test_sql_query_tool_blocked():
    # Verify SQL query tool blocks modifications
    res = tools.run_sql_query("INSERT INTO users (email) VALUES ('hacker@test.com')")
    assert "error" in res[0]
    assert "SELECT" in res[0]["error"]
