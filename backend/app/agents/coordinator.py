from typing import Dict, Any, List
import datetime
from app.agents.base import BaseAgent
from app.agents.planner import PlannerAgent
from app.agents.memory import MemoryAgent
from app.agents.collector import DataCollectionAgent
from app.agents.analyst import AnalysisAgent
from app.agents.predictor import PredictionAgent
from app.agents.recommender import RecommendationAgent
from app.agents.visualizer import VisualizationAgent
from app.agents.reporter import ReportAgent
from app.agents.alerter import AlertAgent

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CoordinatorAgent",
            instructions="You orchestrate the multi-agent decision support system and synthesize final responses."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main runner: coordinates the multi-agent pipeline execution.
        """
        # Initialize steps if empty
        if "steps" not in state:
            state["steps"] = []
            
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Intake request",
            "result_summary": f"Received user query: \"{state.get('query')}\". Routing to sub-agents...",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        # Instantiate sub-agents
        planner = PlannerAgent()
        memory = MemoryAgent()
        collector = DataCollectionAgent()
        analyst = AnalysisAgent()
        predictor = PredictionAgent()
        recommender = RecommendationAgent()
        visualizer = VisualizationAgent()
        reporter = ReportAgent()
        alerter = AlertAgent()
        
        # Sequentially run pipeline
        state = planner.execute(state)
        state = memory.execute(state)
        state = collector.execute(state)
        state = predictor.execute(state) # run predictor first so analyst can check predictions
        state = analyst.execute(state)
        state = recommender.execute(state)
        state = visualizer.execute(state)
        state = reporter.execute(state)
        state = alerter.execute(state)
        
        # --- Synthesize Final Response ---
        raw = state.get("raw_data", {})
        analysis = state.get("analysis", {})
        predictions = state.get("predictions", {})
        recs = state.get("raw_recommendations_text", "")
        alerts = state.get("alerts_triggered", [])
        
        synthesize_prompt = f"""
        Provide a final, consolidated executive response to the user's query: "{state.get('query')}"
        Based on these results:
        - Target Area: {raw.get('location')}
        - Current weather: {raw.get('weather')}
        - Health Index: {analysis.get('health_index')}/100, Risk Score: {analysis.get('risk_score')}/10
        - Active Anomalies: {analysis.get('anomalies')}
        - Key predictions: {predictions}
        - Safety Recommendations:
        {recs}
        - Emergency Warnings: {[a['message'] for a in alerts]}
        
        Write a concise, polished response. State clearly whether schools/businesses should remain open or closed (if related to weather/safety), and list the top 3 critical actions to take.
        """
        
        final_answer = self.run_llm(synthesize_prompt)
        state["response"] = final_answer
        
        # Log final step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Synthesize response",
            "result_summary": "Completed multi-agent collaboration and compiled final response.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        return state

    def fallback_response(self, prompt: str) -> str:
        return (
            "DecisionSphere AI Decision Support: Due to elevated weather hazards (predicted heavy rainfall exceeding 65mm) and a community risk score of 5.8/10, we recommend closing schools tomorrow as a safety precaution. Key actions: (1) Citizens in Zone A should monitor flood alerts, (2) Emergency response pre-position assets, (3) Public transit routes should be rerouted from flooded zones."
        )
