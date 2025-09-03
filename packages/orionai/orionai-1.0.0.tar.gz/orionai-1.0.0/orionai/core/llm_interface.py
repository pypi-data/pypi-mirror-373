"""
LLM Interface for OrionAI
=========================

Provides pluggable interface for different LLM providers (OpenAI, Anthropic, etc.)
with the specific prompt structure designed for safe code generation.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, List

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Protocol for LLM providers."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM."""
        ...


class OpenAIProvider:
    """OpenAI GPT provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        # Lazy import to prevent blocking on module load
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0),  # Deterministic by default
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise


class AnthropicProvider:
    """Anthropic Claude provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("anthropic package required for AnthropicProvider")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise


class GoogleProvider:
    """Google Gemini provider implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Configure safety settings to be less restrictive
            safety_settings = [
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
            
            self.model = genai.GenerativeModel(
                model_name=model,
                safety_settings=safety_settings
            )
            self.model_name = model
        except ImportError:
            raise ImportError("google-generativeai package required for GoogleProvider")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using Google Gemini API."""
        try:
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2000),
                "top_k": 40,
                "top_p": 0.95,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Handle cases where response is blocked or empty
            if not response.candidates:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your request."
            
            candidate = response.candidates[0]
            
            # Check if content was blocked
            if candidate.finish_reason.name in ["SAFETY", "RECITATION"]:
                return "I apologize, but I cannot generate this content due to safety policies. Please try a different request."
            
            # Check if we have valid content
            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                return candidate.content.parts[0].text
            else:
                return "I apologize, but I couldn't generate a proper response. Please try again."
                
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            # Return a more user-friendly error message
            if "finish_reason" in str(e):
                return "I apologize, but the content was filtered by safety policies. Please try rephrasing your request."
            return f"I encountered an error: {str(e)}. Please try again."


class LLMInterface:
    """
    Main LLM interface that implements the OrionAI prompt structure.
    """
    
    # Core system prompt for object-based operations
    SYSTEM_PROMPT = """You are OrionAI, an AI coding assistant.
Your role is to translate user queries into SAFE Python code snippets
that operate on the provided object context. 

RULES:
1. Always return VALID Python code inside triple backticks.
2. Never invent column names, methods, or functions.
3. Use only the provided object context.
4. If the query cannot be answered, reply with: "Not possible with current object."
5. Output format must include:
   - `explanation`: short description of what code does.
   - `code`: the Python code (inside ```python).
   - `expected_output`: structured description of what user will see.

Return your response in JSON format:
{
  "explanation": "...",
  "code": "```python\\n...\\n```",
  "expected_output": "..."
}"""

    # General chat prompt for flexible interactions
    CHAT_PROMPT = """You are OrionAI, a helpful AI coding assistant.

You can help with:
- Writing Python code for any task
- Explaining programming concepts
- Debugging and fixing code issues
- Data analysis and visualization
- General programming questions

When providing code examples:
1. Use proper Python syntax
2. Include helpful comments
3. Provide complete, runnable code
4. Explain what the code does

If the user asks for code, provide it in Python code blocks using ```python syntax.
Be helpful, accurate, and educational in your responses."""
    
    def __init__(self, provider: Optional[LLMProvider] = None):
        """
        Initialize LLM interface.
        
        Args:
            provider: LLM provider instance (defaults to OpenAI)
        """
        self.provider = provider or OpenAIProvider()
        logger.info(f"LLMInterface initialized with {type(self.provider).__name__}")
    
    def generate_chat_response(self, query: str, conversation_history: List[Dict[str, str]] = None, **kwargs) -> str:
        """
        Generate a chat response for general queries.
        
        Args:
            query: User's query
            conversation_history: Previous conversation messages
            **kwargs: Additional parameters for LLM
            
        Returns:
            LLM response text
        """
        # Build conversation context
        messages = []
        
        # Add system message
        messages.append({"role": "system", "content": self.CHAT_PROMPT})
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append(msg)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        # Build prompt for providers that don't support messages
        if isinstance(self.provider, GoogleProvider):
            # Google provider needs a single prompt
            prompt_parts = [self.CHAT_PROMPT]
            
            if conversation_history:
                prompt_parts.append("\nConversation History:")
                for msg in conversation_history[-5:]:
                    role = "Human" if msg["role"] == "user" else "Assistant"
                    prompt_parts.append(f"{role}: {msg['content']}")
            
            prompt_parts.append(f"\nHuman: {query}")
            prompt_parts.append("\nAssistant:")
            
            prompt = "\n".join(prompt_parts)
        else:
            # For OpenAI and Anthropic, use the query with system context
            prompt = f"{self.CHAT_PROMPT}\n\nUser: {query}\n\nAssistant:"
        
        try:
            response = self.provider.generate(prompt, **kwargs)
            logger.debug(f"Chat response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def generate_code(self, query: str, context: Dict[str, Any], **kwargs) -> str:
        """
        Generate Python code for the given query and context.
        
        Args:
            query: User's natural language query
            context: Object metadata and context
            **kwargs: Additional parameters for LLM
            
        Returns:
            JSON string with explanation, code, and expected output
        """
        prompt = self._build_prompt(query, context)
        
        try:
            response = self.provider.generate(prompt, **kwargs)
            logger.debug(f"LLM response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            # Return fallback response
            return json.dumps({
                "explanation": "Error occurred during code generation",
                "code": "```python\\n# Error: Could not generate code\\npass\\n```",
                "expected_output": "Error message"
            })
    
    def explain_object(self, metadata: Dict[str, Any]) -> str:
        """
        Generate explanation of object structure and content.
        
        Args:
            metadata: Object metadata
            
        Returns:
            Human-readable explanation
        """
        prompt = f"""Explain the following object in simple terms:

Object Type: {metadata.get('type', 'Unknown')}
Metadata: {json.dumps(metadata, indent=2)}

Provide a clear, concise explanation of what this object contains and what operations might be useful."""
        
        try:
            return self.provider.generate(prompt, temperature=0.3)
        except Exception as e:
            logger.error(f"Error explaining object: {str(e)}")
            return f"Unable to explain {metadata.get('type', 'object')} due to error."
    
    def _build_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """
        Build the complete prompt following OrionAI template.
        
        Args:
            query: User query
            context: Context dictionary
            
        Returns:
            Complete prompt string
        """
        # Extract metadata
        object_metadata = context.get("object_metadata", {})
        previous_queries = context.get("previous_queries", [])
        
        # Build context section
        context_section = f"""Object Type: {object_metadata.get('type', 'Unknown')}
Object Metadata: {json.dumps(object_metadata, indent=2)}"""
        
        # Add previous queries if available
        if previous_queries:
            history = "\\n".join([
                f"- {q['query']} -> {q['explanation']}" 
                for q in previous_queries[-3:]  # Last 3 queries
            ])
            context_section += f"\\n\\nPrevious Queries:\\n{history}"
        
        # Complete prompt
        prompt = f"""{self.SYSTEM_PROMPT}

User Query:
{query}

Context:
{context_section}

Instruction:
Translate user request into safe Python code operating ONLY on the given context.
Use 'obj' as the variable name for the main object.

Return in JSON format as specified above."""
        
        return prompt
