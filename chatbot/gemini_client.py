"""
Simple Gemini API client for construction chatbot.
"""
import google.generativeai as genai
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str, model_name: str = 'gemini-1.5-flash'):
        """Initialize Gemini client."""
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Generation config
        self.generation_config = {
            "temperature": 0.0,
            "top_p": 1.0,
            "max_output_tokens": 2048,
            "candidate_count": 1
        }
    
    def generate_response(self, 
                         prompt: str, 
                         conversation_history: Optional[List[Dict]] = None,
                         system_prompt: Optional[str] = None) -> str:
        """Generate response from Gemini API."""
        try:
            # Build conversation context
            context = []
            
            if system_prompt:
                context.append(f"System: {system_prompt}")
            
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    context.append(f"{role.capitalize()}: {content}")
            
            # Add current prompt
            context.append(f"User: {prompt}")
            
            # Join all context
            full_prompt = "\n".join(context)
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            if response.text:
                return response.text
            else:
                # Handle blocked content or other issues
                logger.warning("No response text generated")
                return "I'm sorry, I couldn't generate a response for that query."
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    def generate_sql_query(self, 
                           user_request: str, 
                           schema_info: str) -> str:
        """Generate SQL query based on user request and schema."""
        sql_prompt = f"""You are a SQL expert for a construction project management database.

Database Schema:
{schema_info}

User Request: {user_request}

Generate a SQL query to answer this request. Follow these rules **exactly**:
1. Only use SELECT statements.
2. Wrap **every** table and column name in double quotes exactly as shown in the schema 
   (e.g. "projects"."createdAt", "phases"."status").
3. Include appropriate JOIN, WHERE, and ORDER BY clauses.
5. Use proper PostgreSQL syntax.
6. Handle NULL values appropriately.
7. Use table aliases (also quoted) for readability.

Provide **only** the SQL query, no explanation:"""

        try:
            response = self.model.generate_content(
                sql_prompt,
                generation_config={
                    "temperature": 0.3,   # Lower temperature for precise SQL
                    "max_output_tokens": 1024
                }
            )
            # Strip any leading/trailing whitespace or code fences
            return response.text.strip().strip("```").strip()
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise
    
    def format_query_results(self, 
                            user_request: str, 
                            query: str, 
                            results: List[Dict]) -> str:
        """Format query results into natural language response."""
        format_prompt = f"""Format these database query results into a natural, conversational response.

User's Question: {user_request}
SQL Query Used: {query}
Results: {results}

Requirements:
1. Present information clearly and concisely
2. Use markdown formatting (tables, bold, bullets)
3. Add visual elements like progress bars for percentages if applicable
4. Organize data logically with headings if needed
5. Make it easy to scan and understand
6. If there are no results, explain why clearly 
7. If there are too many results, summarize key points

Format the response:"""
        
        try:
            response = self.model.generate_content(
                format_prompt,
                generation_config={
                    "temperature": 0.0,
                    "max_output_tokens": 2048
                }
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error formatting results: {e}")
            return f"I found {len(results)} results but had trouble formatting them."
    
    def analyze_query_intent(self, user_message: str, schema_info: str) -> Dict:
        """Analyze user query to determine if SQL is needed."""
        intent_prompt = f"""Analyze this user message to determine if a database query is needed.

User Message: {user_message}
Available Database: {schema_info}

Respond with JSON format:
{{
    "needs_database": true/false,
    "explanation": "brief explanation of why database is or isn't needed",
    "suggested_approach": "how to handle this query"
}}"""
        
        try:
            response = self.model.generate_content(
                intent_prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 512
                }
            )
            
            # Parse JSON response
            import json
            try:
                return json.loads(response.text.strip())
            except json.JSONDecodeError:
                # If JSON parsing fails, return default
                return {
                    "needs_database": True,
                    "explanation": "Defaulting to database query",
                    "suggested_approach": "Execute database query"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing query intent: {e}")
            # Default to database query on error
            return {
                "needs_database": True,
                "explanation": f"Error in analysis: {e}",
                "suggested_approach": "Execute database query"
            }