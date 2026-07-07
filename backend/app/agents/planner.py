from typing import Dict, Any, List
import datetime
from app.agents.base import BaseAgent

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PlannerAgent",
            instructions="You break down complex queries into subtasks, selecting appropriate specialized agents."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query", "")
        
        # --- Generate plan details via Gemini ---
        planner_prompt = f"""
        Break down this urban decision request: "{query}"
        Identify:
        1. What datasets/APIs are required.
        2. What ML models should be run.
        3. Which agents are required.
        4. The recommended execution sequence.
        
        Output a structured list of subtasks.
        """
        
        plan_desc = self.run_llm(planner_prompt)
        
        # Standard sequential pipeline sequence
        sequence = [
            "MemoryAgent", 
            "DataCollectionAgent", 
            "AnalysisAgent", 
            "PredictionAgent", 
            "RecommendationAgent", 
            "VisualizationAgent", 
            "ReportAgent", 
            "AlertAgent"
        ]
        
        state["plan"] = {
            "query_analysis": plan_desc,
            "agent_sequence": sequence,
            "scheduled_at": datetime.datetime.utcnow().isoformat()
        }
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Deconstruct query & map workflow",
            "result_summary": f"Identified sequence of {len(sequence)} collaborating agents to address user requirements.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "Plan generated: [Memory -> Collect -> Analyze -> Predict -> Recommend -> Visualize -> Report -> Alert]."
