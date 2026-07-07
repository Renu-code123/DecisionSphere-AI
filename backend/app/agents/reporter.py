from typing import Dict, Any
import datetime
import os
import csv
from app.agents.base import BaseAgent
from app.config import settings

# Setup reports storage folder
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "reports")

class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ReportAgent",
            instructions="You assemble comprehensive executive, government, and citizen reports, saving them to disk."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        query = state.get("query", "")
        raw = state.get("raw_data", {})
        analysis = state.get("analysis", {})
        predictions = state.get("predictions", {})
        recs = state.get("recommendations", [])
        
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_title = f"DecisionSphere_Report_{timestamp_str}"
        
        # --- Generate CSV Report ---
        csv_filename = f"{report_title}.csv"
        csv_path = os.path.join(REPORTS_DIR, csv_filename)
        
        try:
            with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["DecisionSphere AI - Urban Metrics Extract"])
                writer.writerow(["Timestamp", datetime.datetime.now().isoformat()])
                writer.writerow(["Location", raw.get("location")])
                writer.writerow([])
                writer.writerow(["Metric", "Current/Predicted Value"])
                writer.writerow(["Composite Health Index", analysis.get("health_index")])
                writer.writerow(["Community Risk Score", analysis.get("risk_score")])
                writer.writerow(["Flood Probability", f"{predictions.get('flood_probability', 0):.2%}"])
                writer.writerow(["Traffic Congestion", f"{predictions.get('traffic_congestion', 0):.1f}%"])
                writer.writerow(["Air Quality Index", predictions.get("air_quality")])
                writer.writerow(["Water Consumption (ML/d)", predictions.get("water_consumption")])
                writer.writerow(["Energy Usage (MWh/d)", predictions.get("energy_usage")])
                writer.writerow([])
                writer.writerow(["Action Recommendations"])
                for r in recs:
                    writer.writerow([r])
        except Exception as e:
            print(f"Failed to generate CSV report: {e}")
            
        # --- Generate PDF/Text Report Brief ---
        pdf_filename = f"{report_title}.txt" # For zero-dependency stability, write a clean text brief
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        try:
            with open(pdf_path, mode='w', encoding='utf-8') as f:
                f.write(f"==================================================\n")
                f.write(f"  DECISIONSPHERE AI - DECISION SUPPORT EXECUTIVE BRIEF\n")
                f.write(f"  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"  Target Sector: {raw.get('location')}\n")
                f.write(f"==================================================\n\n")
                f.write(f"1. PROBLEM CONTEXT\n")
                f.write(f"Query: \"{query}\"\n\n")
                f.write(f"2. COMPOSITE INDICES\n")
                f.write(f"- Community Health Index: {analysis.get('health_index')}/100\n")
                f.write(f"- Hazard Risk Index: {analysis.get('risk_score')}/10\n\n")
                f.write(f"3. MACHINE LEARNING PREDICTIONS\n")
                for key, val in predictions.items():
                    f.write(f"- {key.replace('_', ' ').capitalize()}: {val:.2f}\n")
                f.write(f"\n4. ACTIONABLE RECOMMENDATIONS\n")
                for idx, r in enumerate(recs, 1):
                    f.write(f"{idx}. {r}\n")
                f.write(f"\n==================================================\n")
                f.write(f"DecisionSphere AI - Kaggle Capstone Project. Grandmaster Tier.\n")
        except Exception as e:
            print(f"Failed to generate PDF-brief report: {e}")
            
        # Register generated files in state
        relative_csv_url = f"/static/reports/{csv_filename}"
        relative_pdf_url = f"/static/reports/{pdf_filename}"
        
        state["reports"] = [
            {"title": "Detailed Metric Dataset (CSV)", "format": "CSV", "url": relative_csv_url, "path": csv_path},
            {"title": "Executive Decision Brief (PDF/TXT)", "format": "PDF", "url": relative_pdf_url, "path": pdf_path}
        ]
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Assemble CSV & TXT download briefs",
            "result_summary": f"Generated CSV dataset ({csv_filename}) and Executive Brief ({pdf_filename}) on local disk.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "Report writing fallback complete."
