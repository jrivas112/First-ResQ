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
        # Optimized model preferences for Snapdragon X-Elite processors
        # Prioritizing models that leverage X-Elite's NPU and on-device AI capabilities
        self.preferred_models = [
            "llama3.2:3b",      # Optimized for X-Elite NPU acceleration
            "phi3.5:3.8b",      # Microsoft's X-Elite optimized model
            "qwen2.5:3b",       # Efficient reasoning for edge devices
            "mistral:7b",       # Balanced performance on X-Elite
            "gemma2:2b",        # Google's edge-optimized model
            "phi3:mini",        # Fallback for lower memory scenarios
            "qwen2:1.5b"        # Ultra-fast emergency response model
        ]  # Order by speed and preference
        self.conversation_histories = {}  # Dictionary to store per-profile conversation histories
        self.current_profile_id = "guest"  # Default profile ID
        
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
        """Get the best available model optimized for Snapdragon X-Elite NPU"""
        # Check for X-Elite NPU optimization environment variable
        use_npu = os.getenv('SNAPDRAGON_NPU_ENABLED', 'false').lower() == 'true'
        
        if use_npu:
            print("🧠 Snapdragon X-Elite NPU acceleration enabled")
            # Prioritize models optimized for X-Elite NPU
            npu_optimized_models = [
                "llama3.2:3b",      # X-Elite NPU optimized
                "phi3.5:3.8b",      # Microsoft X-Elite model
                "qwen2.5:3b"        # Edge-optimized for NPU
            ]
            for model in npu_optimized_models:
                if model in self.available_models:
                    print(f"🚀 Using X-Elite optimized model: {model}")
                    return model
        
        # Standard model selection for non-X-Elite systems
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
                    "num_predict": 800  # Increased for comprehensive first aid instructions
                }
            elif "qwen2" in model.lower():
                options = {
                    "temperature": 0.5,     # Lower for faster, very focused responses
                    "top_p": 0.85,         # Slightly more focused
                    "top_k": 10,           # Very fast token selection
                    "num_predict": 600,    # Increased for detailed medical responses
                    "repeat_penalty": 1.15  # Prevent repetition in small model
                }
                # Ultra-fast mode for qwen2
            elif "phi3" in model.lower():
                options = {
                    "temperature": 0.6,     # Slightly lower for faster, more focused responses
                    "top_p": 0.9,
                    "top_k": 15,           # Faster token selection
                    "num_predict": 700,    # Increased for complete first aid instructions
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
                
                # Debug logging - show complete prompt being sent to Ollama
                print(f"=== OLLAMA PROMPT DEBUG ===")
                print(f"Model: {model}")
                print(f"Options: {options}")
                print(f"Prompt length: {len(prompt)} chars")
                print(f"=== FULL PROMPT TO OLLAMA ===")
                print(prompt)
                print(f"=== END OF PROMPT ===")
                print(f"Response length: {len(full_response)} chars")
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
    
    def get_answer(self, query: str, profile_info: Dict = None, profile_id: str = "guest", similarity_threshold: float = 0.1) -> Dict:
        """Get enhanced answer using RAG + Ollama with smart conversation context"""
        # Set the current profile for this request
        self.set_current_profile(profile_id)
        
        # Store original query for history (without profile info)
        original_query = query
        
        # Check if this is just a greeting first
        if self.is_greeting(query):
            greeting_response = self.get_greeting_response(query)
            # Don't store greetings in conversation history
            return greeting_response
        
        # Add conversation context if this seems like a follow-up question
        contextual_query = self.add_conversation_context(query)
        
        similar_questions = self.search_similar_questions(contextual_query, top_k=3)
        
        # Try Ollama-enhanced response first (with profile context)
        ollama_response = self.get_ollama_enhanced_answer(contextual_query, similar_questions, profile_info)
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
        result = {
            "answer": best_match['answer'],
            "confidence": best_match['similarity'],
            "source": f"Question {best_match['index']}: {best_match['question'][:100]}...",
            "similar_questions": [q['question'][:80] + "..." if len(q['question']) > 80 else q['question'] for q in similar_questions[:3]],
            "method": "rag_only"
        }
        
        # Update conversation history for RAG-only responses too
        self.update_conversation_history(original_query, result['answer'])
        return result
    
    def get_ollama_enhanced_answer(self, query: str, similar_questions: List[Dict], profile_info: Dict = None) -> Dict:
        """Get answer using Ollama with RAG context and profile information"""
        # Debug: Show what profile info we received
        print(f"=== PROFILE INFO DEBUG ===")
        print(f"Profile info received: {profile_info}")
        print(f"Query: {query}")
        print(f"Current profile ID: {getattr(self, 'current_profile_id', 'Not set')}")
        
        # Create profile context string if profile info is provided
        profile_context = ""
        if profile_info:
            profile_context = f"""Patient Information:
- Age: {profile_info.get('age', 'N/A')}
- Gender: {profile_info.get('gender', 'N/A')}
- Blood Group: {profile_info.get('blood_group', 'N/A')}
- Pre-existing Conditions: {profile_info.get('pre_existing_conditions', 'None')}

Please consider these details when providing your response.

"""
            print(f"=== PROFILE CONTEXT CREATED ===")
            print(profile_context)
            print(f"⚠️  NOTE: Profile information will be used for context but filtered from response")
        
        if not similar_questions or similar_questions[0]['similarity'] < 0.05:
            # No good matches, use Ollama alone
            prompt = f"""You are a helpful first aid assistant. Please provide a clear, practical response to this first aid question (keep answers to 150-200 words):

{profile_context}{query}

IMPORTANT: Do NOT mention or repeat any patient information (age, gender, blood group, conditions) in your response. Use this information only as context to tailor your advice appropriately.

Format your response using valid HTML with:
- Use <h3> for section headings
- Use <ol> or <ul> for step-by-step instructions
- Use <strong> for important warnings or key points
- Use <p> for paragraphs
- Use <em> for emphasis when needed

Provide specific steps and safety information. If this is a serious emergency, advise seeking immediate medical help."""
            
            ollama_response = self.query_ollama(prompt)
            if ollama_response:
                sanitized_response = self.sanitize_response(ollama_response.strip(), profile_info)
                return {
                    "answer": sanitized_response,
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

{profile_context}Now answer this question with clear, practical steps:

{query}

IMPORTANT: Do NOT mention or repeat any patient information (age, gender, blood group, conditions) in your response. Use this information only as context to tailor your advice appropriately.

Format your response using valid HTML with:
- Use <h3> for section headings
- Use <ol> or <ul> for step-by-step instructions  
- Use <strong> for important warnings or key points
- Use <p> for paragraphs
- Use <em> for emphasis when needed

Use the knowledge base information and expand on it with helpful details."""
            
            ollama_response = self.query_ollama(prompt)
            if ollama_response:
                sanitized_response = self.sanitize_response(ollama_response.strip(), profile_info)
                return {
                    "answer": sanitized_response,
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
                print(f"❌ Model {best_model} failed to respond")
                return False
        except Exception as e:
            print(f"Failed to connect to Ollama: {e}")
            return False
