import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from typing import List, Dict, Tuple

class FirstAidRAG:
    def __init__(self, csv_path: str = "firstaidqa-00000-of-00001 (1).csv"):
        self.csv_path = csv_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, lightweight model
        self.df = None
        self.embeddings = None
        self.embeddings_file = "question_embeddings.pkl"
        
    def load_data(self):
        """Load the CSV data"""
        print("Loading first aid dataset...")
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} Q&A pairs")
        
    def generate_embeddings(self, force_regenerate: bool = False):
        """Generate embeddings for all questions"""
        if os.path.exists(self.embeddings_file) and not force_regenerate:
            print("Loading cached embeddings...")
            with open(self.embeddings_file, 'rb') as f:
                self.embeddings = pickle.load(f)
        else:
            print("Generating embeddings for questions...")
            questions = self.df['question'].tolist()
            self.embeddings = self.model.encode(questions)
            
            # Cache embeddings for faster startup next time
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            print("Embeddings cached for future use")
    
    def search_similar_questions(self, query: str, top_k: int = 3) -> List[Dict]:
        """Find the most similar questions to the user query"""
        # Generate embedding for the query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k most similar questions
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
    
    def get_answer(self, query: str, similarity_threshold: float = 0.3) -> Dict:
        """Get the best answer for a query"""
        similar_questions = self.search_similar_questions(query, top_k=1)
        
        if not similar_questions or similar_questions[0]['similarity'] < similarity_threshold:
            return {
                "answer": "I'm sorry, I don't have specific information about that. Please consult a medical professional or call emergency services if this is urgent.",
                "confidence": 0.0,
                "source": "fallback"
            }
        
        best_match = similar_questions[0]
        return {
            "answer": best_match['answer'],
            "confidence": best_match['similarity'],
            "source": f"Question {best_match['index']}: {best_match['question'][:100]}...",
            "similar_questions": [q['question'] for q in similar_questions[:3]]
        }
    
    def initialize(self):
        """Initialize the RAG system"""
        self.load_data()
        self.generate_embeddings()
        print("First Aid RAG system ready!")

# Usage example
if __name__ == "__main__":
    # Initialize the system
    rag = FirstAidRAG()
    rag.initialize()
    
    # Test queries
    test_queries = [
        "How do I treat a burn?",
        "What should I do if someone is choking?",
        "My child fell and hurt their arm",
        "Someone is bleeding heavily"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = rag.get_answer(query)
        print(f"📋 Confidence: {result['confidence']:.2f}")
        print(f"💡 Answer: {result['answer'][:200]}...")
        print(f"📚 Source: {result['source']}")
