import requests
import json
from typing import List, Dict
import os

class LocalRAGService:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.qdrant_url = os.getenv("QDRANT_HOST", "http://localhost:6333")
    
    def chat_with_ollama(self, prompt: str, model: str = "llama2") -> str:
        """Chat with local Ollama LLM"""
        try:
            response = requests.post(
                f"http://{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.status_code == 200:
                return response.json().get("response", "No response")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Connection error: {str(e)}"
    
    def store_document_in_qdrant(self, text: str, collection_name: str = "documents"):
        """Store document in Qdrant vector database"""
        # This is a simplified example - in practice you'd use proper embeddings
        try:
            # Create collection if it doesn't exist
            requests.put(
                f"http://{self.qdrant_url}/collections/{collection_name}",
                json={
                    "vectors": {
                        "size": 384,  # Adjust based on your embedding model
                        "distance": "Cosine"
                    }
                }
            )
            
            # In practice, you'd generate proper embeddings here
            # For demo purposes, using dummy vector
            dummy_vector = [0.1] * 384
            
            response = requests.put(
                f"http://{self.qdrant_url}/collections/{collection_name}/points",
                json={
                    "points": [{
                        "id": hash(text) % 1000000,
                        "vector": dummy_vector,
                        "payload": {"text": text}
                    }]
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error storing document: {e}")
            return False
    
    def search_documents(self, query: str, collection_name: str = "documents") -> List[Dict]:
        """Search for relevant documents in Qdrant"""
        try:
            # In practice, you'd convert query to embeddings
            dummy_vector = [0.1] * 384
            
            response = requests.post(
                f"http://{self.qdrant_url}/collections/{collection_name}/points/search",
                json={
                    "vector": dummy_vector,
                    "limit": 3,
                    "with_payload": True
                }
            )
            
            if response.status_code == 200:
                return response.json().get("result", [])
            return []
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def rag_query(self, question: str) -> str:
        """Perform RAG: Retrieve relevant docs and generate answer"""
        # 1. Search for relevant documents
        relevant_docs = self.search_documents(question)
        
        # 2. Combine docs into context
        context = "\n".join([doc.get("payload", {}).get("text", "") 
                           for doc in relevant_docs])
        
        # 3. Create prompt with context
        prompt = f"""
        Context: {context}
        
        Question: {question}
        
        Please answer the question based on the provided context.
        """
        
        # 4. Generate answer using LLM
        return self.chat_with_ollama(prompt)

# Usage example
if __name__ == "__main__":
    rag = LocalRAGService()
    
    # Store some documents
    rag.store_document_in_qdrant("First aid for burns: Cool the burn with water for 10 minutes.")
    rag.store_document_in_qdrant("For bleeding: Apply direct pressure and elevate the wound.")
    
    # Perform RAG query
    answer = rag.rag_query("How do I treat a burn?")
    print(answer)
