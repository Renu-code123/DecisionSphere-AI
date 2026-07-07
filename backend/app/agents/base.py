from typing import Dict, Any, List
import datetime
from google import genai
from app.config import settings

class BaseAgent:
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions
        self.client = None
        
        # Initialize Gemini Client if Key is available
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Gemini Client for agent {name}: {e}")

    def run_llm(self, prompt: str, system_instruction: str = None) -> str:
        """
        Helper method to run a query against Gemini.
        Falls back to a deterministic rule-based mock if GEMINI_API_KEY is not set.
        """
        sys_inst = system_instruction or self.instructions
        if self.client:
            try:
                # Call Gemini model
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"system_instruction": sys_inst}
                )
                return response.text
            except Exception as e:
                return f"[Gemini Error fallback] Error calling Gemini: {e}\nPrompt: {prompt}"
        else:
            return self.fallback_response(prompt)

    def fallback_response(self, prompt: str) -> str:
        """
        Default rule-based mock response when Gemini API key is missing.
        Subclasses should override this for domain-specific defaults.
        """
        return f"[Mock Offline Mode] Agent {self.name} received prompt: {prompt}"
        
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the agent logic.
        Updates and returns the shared agent state.
        """
        raise NotImplementedError("Each agent must implement its own execute method.")
