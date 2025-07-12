import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import re
import requests
from typing import List, Dict

class EnhancedFirstAidRAG:
    def __init__(self, csv_path: str = "firstaidqa-00000-of-00001 (1).csv", ollama_host: str = "ollama:11434"):
        self.csv_path = csv_path
        self.ollama_host = ollama_host
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.df = None
        self.question_vectors = None
        self.vectors_file = "question_vectors.pkl"
        
    def preprocess_text(self, text: str) -> str:
        """Simple text preprocessing"""
        text = re.sub(r'\s+', ' ', text.strip())
        text = text.replace('"', '').replace("'", "")
        return text.lower()
        
    def load_data(self):
        """Load the CSV data"""
        print("Loading first aid dataset...")
        self.df = pd.read_csv(self.csv_path)
        
        # Clean the data
        self.df['question'] = self.df['question'].apply(self.preprocess_text)
        self.df['answer'] = self.df['answer'].apply(self.preprocess_text)
        
        print(f"Loaded {len(self.df)} Q&A pairs")
        
    def generate_vectors(self, force_regenerate: bool = False):
        """Generate TF-IDF vectors for all questions"""
        if os.path.exists(self.vectors_file) and not force_regenerate:
            print("Loading cached vectors...")
            with open(self.vectors_file, 'rb') as f:
                data = pickle.load(f)
                self.question_vectors = data['vectors']
                self.vectorizer = data['vectorizer']
        else:
            print("Generating TF-IDF vectors for questions...")
            questions = self.df['question'].tolist()
            self.question_vectors = self.vectorizer.fit_transform(questions)
            
            # Cache vectors for faster startup next time
            with open(self.vectors_file, 'wb') as f:
                pickle.dump({
                    'vectors': self.question_vectors,
                    'vectorizer': self.vectorizer
                }, f)
            print("Vectors cached for future use")
    
    def search_similar_questions(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find the most similar questions to the user query"""
        processed_query = self.preprocess_text(query)
        query_vector = self.vectorizer.transform([processed_query])
        
        similarities = cosine_similarity(query_vector, self.question_vectors)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'question': self.df.iloc[idx]['question'],
                'answer': self.df.iloc[idx]['answer'],
                'similarity': float(similarities[idx]),
                'index': int(idx)
            })
        
        return results
    
    def query_ollama(self, prompt: str, model: str = "phi3:mini") -> str:
        """Query Ollama LLM"""
        try:
            response = requests.post(
                f"http://{self.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200,  # Use num_predict instead of max_tokens
                        "top_p": 0.9,
                        "stop": ["\n\n"]  # Stop at double newline for concise responses
                    }
                },
                timeout=15  # Reduced timeout to 15 seconds
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"Ollama error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.Timeout:
            print("Ollama request timed out (15s)")
            return None
        except Exception as e:
            print(f"Failed to connect to Ollama: {e}")
            return None
    
    def get_answer(self, query: str, similarity_threshold: float = 0.1) -> Dict:
        """Get enhanced answer using RAG + Ollama"""
        similar_questions = self.search_similar_questions(query, top_k=3)
        
        # Try Ollama-enhanced response first
        ollama_response = self.get_ollama_enhanced_answer(query, similar_questions)
        if ollama_response:
            return ollama_response
        
        # Fallback to pure RAG
        if not similar_questions or similar_questions[0]['similarity'] < similarity_threshold:
            return {
                "answer": "I'm sorry, I don't have specific information about that. Please consult a medical professional or call emergency services if this is urgent.",
                "confidence": 0.0,
                "source": "fallback",
                "similar_questions": [],
                "method": "fallback"
            }
        
        best_match = similar_questions[0]
        return {
            "answer": best_match['answer'],
            "confidence": best_match['similarity'],
            "source": f"Question {best_match['index']}: {best_match['question'][:100]}...",
            "similar_questions": [q['question'][:80] + "..." if len(q['question']) > 80 else q['question'] for q in similar_questions[:3]],
            "method": "rag_only"
        }
    
    def get_ollama_enhanced_answer(self, query: str, similar_questions: List[Dict]) -> Dict:
        """Get answer using Ollama with RAG context"""
        if not similar_questions or similar_questions[0]['similarity'] < 0.05:
            # No good matches, use Ollama alone
            prompt = f"""First aid question: {query}

Provide a brief, safe first aid response. If serious, advise seeking medical help.

Answer:"""
            
            ollama_response = self.query_ollama(prompt)
            if ollama_response:
                return {
                    "answer": ollama_response.strip(),
                    "confidence": 0.5,
                    "source": "AI reasoning (no specific match found)",
                    "similar_questions": [],
                    "method": "ollama_only"
                }
        else:
            # Use RAG context with Ollama
            context = similar_questions[0]['answer']  # Just use the best match
            
            prompt = f"""Based on this first aid knowledge: {context}

Question: {query}

Provide a clear, helpful response based on this information.

Answer:"""
            
            ollama_response = self.query_ollama(prompt)
            if ollama_response:
                return {
                    "answer": ollama_response.strip(),
                    "confidence": min(0.9, similar_questions[0]['similarity'] + 0.3),
                    "source": f"AI enhanced with knowledge from similar case",
                    "similar_questions": [q['question'][:80] + "..." if len(q['question']) > 80 else q['question'] for q in similar_questions[:3]],
                    "method": "rag_plus_ollama"
                }
        
        return None  # Ollama failed, will fallback to pure RAG
    
    def initialize(self):
        """Initialize the enhanced RAG system"""
        try:
            self.load_data()
            self.generate_vectors()
            
            # Test Ollama connection and model availability
            print("Testing Ollama connection...")
            test_response = self.test_ollama_connection()
            if test_response:
                print("✅ Enhanced First Aid RAG system ready with Ollama!")
            else:
                print("⚠️  RAG system ready, but Ollama not available (will use RAG-only mode)")
            return True
        except Exception as e:
            print(f"Error initializing enhanced RAG system: {e}")
            return False
    
    def test_ollama_connection(self) -> bool:
        """Test if Ollama is available and has the required model"""
        try:
            # First check if Ollama is responding
            response = requests.get(f"http://{self.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                print(f"Ollama not responding: {response.status_code}")
                return False
            
            # Check if our preferred model is available
            models = response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]
            
            if "phi3:mini" in model_names:
                print("Found phi3:mini model")
                # Test a simple query
                test_result = self.query_ollama("Test", "phi3:mini")
                return test_result is not None
            else:
                print(f"phi3:mini model not found. Available models: {model_names}")
                return False
                
        except Exception as e:
            print(f"Error testing Ollama: {e}")
            return False

# Usage example
if __name__ == "__main__":
    rag = EnhancedFirstAidRAG()
    if rag.initialize():
        test_queries = [
            "How do I treat a burn?",
            "What should I do if someone is choking?",
            "My child fell and hurt their arm",
            "How to stop severe bleeding from a deep cut?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            result = rag.get_answer(query)
            print(f"📋 Confidence: {result['confidence']:.3f}")
            print(f"🤖 Method: {result['method']}")
            print(f"💡 Answer: {result['answer'][:200]}...")
            if result['source'] != 'fallback':
                print(f"📚 Source: {result['source']}")
