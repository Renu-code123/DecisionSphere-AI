from typing import Dict, Any
import datetime
from app.agents.base import BaseAgent
from app.rag.vector_store import vector_store

class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MemoryAgent",
            instructions="You retrieve relevant historical context, user preferences, and disaster guidelines from memory."
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query", "")
        # Query vector store for related guidelines
        related_docs = vector_store.similarity_search(query, k=2)
        
        context_str = ""
        if related_docs:
            context_str = "\n".join([f"- {doc['text']} (Source: {doc['metadata'].get('source', 'System')})" for doc in related_docs])
        else:
            context_str = "No specific guidelines found in vector store."
            
        state["memory_context"] = context_str
        
        # Log step
        state["steps"].append({
            "agent_name": self.name,
            "action_taken": "Search vector memory store",
            "result_summary": f"Retrieved {len(related_docs)} relevant guideline documents.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return state

    def fallback_response(self, prompt: str) -> str:
        return "Memory lookup fallback complete."
