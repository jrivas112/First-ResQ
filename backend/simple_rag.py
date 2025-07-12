import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import re
from typing import List, Dict

class SimpleFirstAidRAG:
    def __init__(self, csv_path: str = "firstaidqa-00000-of-00001 (1).csv"):
        self.csv_path = csv_path
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
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove quotes
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
        # Preprocess and vectorize the query
        processed_query = self.preprocess_text(query)
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.question_vectors)[0]
        
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
    
    def get_answer(self, query: str, similarity_threshold: float = 0.1) -> Dict:
        """Get the best answer for a query"""
        similar_questions = self.search_similar_questions(query, top_k=3)
        
        if not similar_questions or similar_questions[0]['similarity'] < similarity_threshold:
            return {
                "answer": "I'm sorry, I don't have specific information about that. Please consult a medical professional or call emergency services if this is urgent.",
                "confidence": 0.0,
                "source": "fallback",
                "similar_questions": []
            }
        
        best_match = similar_questions[0]
        return {
            "answer": best_match['answer'],
            "confidence": best_match['similarity'],
            "source": f"Question {best_match['index']}: {best_match['question'][:100]}...",
            "similar_questions": [q['question'][:80] + "..." if len(q['question']) > 80 else q['question'] for q in similar_questions[:3]]
        }
    
    def initialize(self):
        """Initialize the RAG system"""
        try:
            self.load_data()
            self.generate_vectors()
            print("Simple First Aid RAG system ready!")
            return True
        except Exception as e:
            print(f"Error initializing RAG system: {e}")
            return False

# Usage example
if __name__ == "__main__":
    # Initialize the system
    rag = SimpleFirstAidRAG()
    if rag.initialize():
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
            print(f"📋 Confidence: {result['confidence']:.3f}")
            print(f"💡 Answer: {result['answer'][:200]}...")
            if result['source'] != 'fallback':
                print(f"📚 Source: {result['source']}")
    else:
        print("Failed to initialize RAG system")
