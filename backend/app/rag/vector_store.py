import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from google import genai
from app.config import settings

STORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vector_store.json")

class LocalVectorStore:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.client = None
        
        # Initialize Gemini Client if Key is available
        if settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Gemini Client for Vector Embeddings: {e}")
                
        self.load()

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generates vector embedding for input text. Uses Gemini model 'text-embedding-004'
        if available, otherwise falls back to a simple bag-of-words tf-idf representation.
        """
        if self.client:
            try:
                # Call Gemini Embedding API
                response = self.client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                return response.embeddings[0].values
            except Exception as e:
                print(f"Embedding API call failed, falling back to heuristic vector: {e}")
        
        # Simple TF-IDF/heuristic vector representation fallback
        # Create a deterministic vocabulary-like hashing index
        words = text.lower().split()
        vector = [0.0] * 128
        for word in words:
            # Hash word into one of 128 dimensions
            idx = hash(word) % 128
            vector[idx] += 1.0
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        docs: List of dicts with {"text": str, "metadata": dict}
        """
        for doc in docs:
            doc_id = doc.get("id", str(len(self.documents)))
            text = doc["text"]
            metadata = doc.get("metadata", {})
            vector = self._get_embedding(text)
            
            # Check if document already exists
            exists = False
            for d in self.documents:
                if d["id"] == doc_id:
                    d["text"] = text
                    d["metadata"] = metadata
                    d["vector"] = vector
                    exists = True
                    break
                    
            if not exists:
                self.documents.append({
                    "id": doc_id,
                    "text": text,
                    "metadata": metadata,
                    "vector": vector
                })
        self.save()

    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs cosine similarity search between query and stored documents.
        """
        if not self.documents:
            return []
            
        query_vector = np.array(self._get_embedding(query))
        
        results = []
        for doc in self.documents:
            doc_vector = np.array(doc["vector"])
            # Cosine similarity
            dot_product = np.dot(query_vector, doc_vector)
            norm_q = np.linalg.norm(query_vector)
            norm_d = np.linalg.norm(doc_vector)
            
            if norm_q > 0 and norm_d > 0:
                score = float(dot_product / (norm_q * norm_d))
            else:
                score = 0.0
                
            results.append({
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": score
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

    def save(self):
        try:
            with open(STORE_FILE, "w") as f:
                # Exclude native float vectors from JSON if they are too big, or save them simply
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            print(f"Failed to save vector store: {e}")

    def load(self):
        if os.path.exists(STORE_FILE):
            try:
                with open(STORE_FILE, "r") as f:
                    self.documents = json.load(f)
            except Exception as e:
                print(f"Failed to load vector store: {e}")
                self.documents = []
        else:
            # Seed with default community documents
            self.seed_default_documents()

    def seed_default_documents(self):
        default_docs = [
            {
                "id": "sop_weather_floods",
                "text": "Standard Operating Procedure (SOP) for Extreme Rain & Flooding: If forecasted rainfall exceeds 50mm in 24 hours, emergency services should monitor low-lying roads. If it exceeds 100mm, local schools must be closed and evacuation shelters opened at community centers. High-risk zones are Zone A (coastal) and Zone C (riverine).",
                "metadata": {"category": "disaster", "source": "City Emergency Council"}
            },
            {
                "id": "policy_traffic_school_closures",
                "text": "School Closure Policy: Decision on closing schools rests with the Municipal Education Board, coordinated with Police & Traffic services. Criteria include: (1) Flood warnings, (2) Air Quality Index (AQI) exceeding 200, (3) Key transport routes blocked by weather or accidents.",
                "metadata": {"category": "education", "source": "Municipal Education Board"}
            },
            {
                "id": "sop_air_pollution_health",
                "text": "Air Quality Emergency Guidelines: When AQI exceeds 150 (Unhealthy), sensitive groups (children, elderly, asthmatics) must avoid outdoor activities. If AQI exceeds 250, industrial activity must reduce output by 30%, and high-efficiency particulate masks should be distributed. Public transport fares are halved to encourage reduced vehicle use.",
                "metadata": {"category": "health", "source": "Environmental Health Dept"}
            },
            {
                "id": "sop_heatwave_water",
                "text": "Heatwave and Water Conservation Plan: During temperatures above 38°C for 3 consecutive days, public cooling centers must operate. Water conservation level 2 is activated: outdoor watering is limited to early mornings (6-8 AM) and odd/even house numbers.",
                "metadata": {"category": "resource", "source": "Water & Climate Authority"}
            }
        ]
        self.add_documents(default_docs)

# Global singleton vector store
vector_store = LocalVectorStore()
