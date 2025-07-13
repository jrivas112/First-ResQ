import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import re
import requests
import json
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
        self.available_models = []
        self.preferred_models = ["qwen2:1.5b", "phi3:mini", "gemma:2b", "mistral:latest", "mistral", "llama2:7b", "llama2"]  # Order by speed and preference
        self.conversation_history = []  # Initialize conversation history
        
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
    
    def get_best_model(self) -> str:
        """Get the best available model from our preferred list"""
        for model in self.preferred_models:
            if model in self.available_models:
                return model
        
        # If none of our preferred models are available, use the first available one
        if self.available_models:
            return self.available_models[0]
        
        # Fallback to phi3:mini (shouldn't happen if we check properly)
        return "phi3:mini"
    
    def query_ollama(self, prompt: str, model: str = None) -> str:
        """Query Ollama LLM"""
        if model is None:
            model = self.get_best_model()
            
        try:
            # Adjust parameters based on model type
            options = {
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Model-specific optimizations for speed and quality
            if "mistral" in model.lower():
                options = {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 20,        # Reduce choices for faster decisions
                    "num_predict": 300  # Limit response length for speed
                }
            elif "qwen2" in model.lower():
                options = {
                    "temperature": 0.5,     # Lower for faster, very focused responses
                    "top_p": 0.85,         # Slightly more focused
                    "top_k": 10,           # Very fast token selection
                    "num_predict": 200,    # Short responses for maximum speed
                    "repeat_penalty": 1.15  # Prevent repetition in small model
                }
                # Ultra-fast mode for qwen2
            elif "phi3" in model.lower():
                options = {
                    "temperature": 0.6,     # Slightly lower for faster, more focused responses
                    "top_p": 0.9,
                    "top_k": 15,           # Faster token selection
                    "num_predict": 250,    # Shorter responses = faster generation
                    "repeat_penalty": 1.1   # Prevent repetition loops
                }
                # Remove stop sequences for phi3 to prevent truncation
            else:
                options["stop"] = ["\n\n"]
            
            # Switch back to /api/generate with proper streaming handling
            response = requests.post(
                f"http://{self.ollama_host}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True,  # Use streaming but handle it properly
                    "options": options
                },
                timeout=30,  # Reduced timeout for faster fallbacks
                stream=True  # Enable streaming in requests 
            )
            
            if response.status_code == 200:
                full_response = ""
                final_data = {}
                
                # Process streaming response line by line
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line.decode('utf-8'))
                            
                            # Accumulate response text
                            if 'response' in chunk_data:
                                full_response += chunk_data['response']
                            
                            # Store final metadata when done
                            if chunk_data.get('done', False):
                                final_data = chunk_data
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                # Debug logging
                print(f"=== OLLAMA GENERATE STREAMING DEBUG ===")
                print(f"Prompt length: {len(prompt)} chars")
                print(f"Model: {model}")
                print(f"Options: {options}")
                print(f"Response length: {len(full_response)} chars")
                print(f"Done: {final_data.get('done', 'unknown')}")
                print(f"Total duration: {final_data.get('total_duration', 'unknown')}")
                print(f"Eval count: {final_data.get('eval_count', 'unknown')}")
                print(f"Full response: '{full_response}'")
                print(f"=== END STREAMING DEBUG ===")
                
                return full_response if full_response else None
            else:
                print(f"Ollama generate error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.Timeout:
            print("Ollama request timed out (15s)")
            return None
        except Exception as e:
            print(f"Failed to connect to Ollama: {e}")
            return None
    
    def get_answer(self, query: str, similarity_threshold: float = 0.1) -> Dict:
        """Get enhanced answer using RAG + Ollama with smart conversation context"""
        # Store original query for history
        original_query = query
        
        # Check if this is just a greeting first
        if self.is_greeting(query):
            greeting_response = self.get_greeting_response(query)
            self.update_conversation_history(original_query, greeting_response['answer'])
            return greeting_response
        
        # Add conversation context if this seems like a follow-up question
        contextual_query = self.add_conversation_context(query)
        
        similar_questions = self.search_similar_questions(contextual_query, top_k=3)
        
        # Try Ollama-enhanced response first
        ollama_response = self.get_ollama_enhanced_answer(contextual_query, similar_questions)
        if ollama_response:
            # Update conversation history with the original query and response
            self.update_conversation_history(original_query, ollama_response['answer'])
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
            prompt = f"""You are a helpful first aid assistant. Please provide a clear, practical response to this first aid question:

{query}

Format your response using valid HTML with:
- Use <h3> for section headings
- Use <ol> or <ul> for step-by-step instructions
- Use <strong> for important warnings or key points
- Use <p> for paragraphs
- Use <em> for emphasis when needed

Provide specific steps and safety information. If this is a serious emergency, advise seeking immediate medical help."""
            
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
            
            prompt = f"""You are a first aid assistant. Based on this relevant information from our knowledge base:

{context}

Now answer this question with clear, practical steps:

{query}

Format your response using valid HTML with:
- Use <h3> for section headings
- Use <ol> or <ul> for step-by-step instructions  
- Use <strong> for important warnings or key points
- Use <p> for paragraphs
- Use <em> for emphasis when needed

Use the knowledge base information and expand on it with helpful details."""
            
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
        """Test if Ollama is available and discover available models"""
        try:
            # First check if Ollama is responding
            response = requests.get(f"http://{self.ollama_host}/api/tags", timeout=5)
            if response.status_code != 200:
                print(f"Ollama not responding: {response.status_code}")
                return False
            
            # Get all available models
            models = response.json().get("models", [])
            self.available_models = [model.get("name", "") for model in models]
            
            if not self.available_models:
                print("No models found in Ollama")
                return False
            
            print(f"Available models: {self.available_models}")
            
            # Find the best model to use
            best_model = self.get_best_model()
            print(f"Selected model: {best_model}")
            
            # Test a simple query with the best model
            test_result = self.query_ollama("Hello", best_model)
            if test_result is not None:
                print(f"✅ Model {best_model} is working")
                return True
            else:
                print(f"❌ Model {best_model} failed test query")
                return False
                
        except Exception as e:
            print(f"Error testing Ollama: {e}")
            return False
    
    def clear_conversation_history(self):
        """Clear conversation history for a fresh start"""
        self.conversation_history = []
        print("Conversation history cleared")
    
    def get_conversation_summary(self) -> Dict:
        """Get a summary of the current conversation"""
        return {
            "total_exchanges": len(self.conversation_history),
            "recent_topics": [q['question'][:50] + "..." if len(q['question']) > 50 else q['question'] 
                            for q in self.conversation_history[-3:]] if self.conversation_history else [],
            "context_enabled": True
        }
    
    def is_greeting(self, query: str) -> bool:
        """Detect if the query is just a greeting or casual conversation"""
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "greetings", "what's up", "how are you", "howdy", "yo", "sup",
            "good day", "hiya", "thanks", "thank you", "bye", "goodbye"
        ]
        
        query_lower = query.lower().strip()
        
        # Check for exact matches or simple variations
        for greeting in greetings:
            if query_lower == greeting or query_lower == greeting + "!" or query_lower == greeting + ".":
                return True
        
        # Check for very short, non-medical queries
        if len(query_lower) <= 3 and query_lower.isalpha():
            return True
            
        return False
    
    def get_greeting_response(self, query: str) -> Dict:
        """Generate a friendly greeting response"""
        friendly_responses = [
            "Hello! I'm QHelper AI, your emergency first aid assistant. How can I help you today?",
            "Hi there! I'm here to help with first aid questions and emergency guidance. What do you need assistance with?",
            "Hello! I'm QHelper AI. Ask me about first aid, emergency procedures, or medical guidance. How can I assist you?",
            "Hi! I'm your first aid assistant. Whether it's treating wounds, handling emergencies, or general health questions - I'm here to help!"
        ]
        
        # Simple hash-based selection for consistency
        response_index = abs(hash(query.lower())) % len(friendly_responses)
        
        return {
            "answer": f"<p>{friendly_responses[response_index]}</p><p><strong>Quick examples:</strong></p><ul><li>\"How do I treat a cut?\"</li><li>\"What should I do if someone is choking?\"</li><li>\"My child has a fever, what should I do?\"</li></ul>",
            "confidence": 1.0,
            "source": "Friendly greeting response",
            "similar_questions": [],
            "method": "greeting"
        }
    
    def detect_follow_up_question(self, query: str) -> bool:
        """Detect if the query is a follow-up question that needs context"""
        follow_up_indicators = [
            "what about", "how about", "what if", "and if", "also",
            "what happens if", "but what", "what should", "how can",
            "what else", "anything else", "more about", "tell me more",
            "what next", "then what", "after that", "also what",
            "but if", "however", "instead", "alternatively"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in follow_up_indicators)
    
    def add_conversation_context(self, query: str) -> str:
        """Add conversation context only if it seems like a follow-up question"""
        if not self.conversation_history or not self.detect_follow_up_question(query):
            return query  # No context needed for fresh questions
        
        # Add context from the most recent Q&A
        recent = self.conversation_history[-1]
        context = f"""Previous conversation context:
Q: {recent['question']}
A: {recent['answer'][:150]}{'...' if len(recent['answer']) > 150 else ''}

Current question: {query}"""
        
        return context
    
    def update_conversation_history(self, question: str, answer: str):
        """Update conversation history with the latest Q&A pair"""
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'timestamp': pd.Timestamp.now()
        })
        
        # Keep only the most recent entries (limit to 5)
        if len(self.conversation_history) > 5:
            self.conversation_history = self.conversation_history[-5:]

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
