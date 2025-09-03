"""
Core AIObject Base Class
========================

The main wrapper class that provides AI-powered natural language interface
to any Python object (DataFrames, Models, Files, etc.).
"""

import json
import logging
from typing import Any, Dict, Optional, Union

from .manager import AdapterManager
from .llm_interface import LLMInterface
from ..utils.sandbox import SafeExecutor
from ..utils.validator import ResponseValidator

logger = logging.getLogger(__name__)


class AIObject:
    """
    AI-enabled wrapper for Python objects that provides natural language interface.
    
    Example:
    --------
    >>> df = pd.DataFrame({'revenue': [100, 200, 300], 'region': ['A', 'B', 'C']})
    >>> ai_df = AIObject(df)
    >>> result = ai_df.ask("Show me average revenue per region")
    """
    
    def __init__(self, obj: Any, llm_interface: Optional[LLMInterface] = None):
        """
        Initialize AIObject wrapper.
        
        Args:
            obj: The Python object to wrap (DataFrame, Model, File, etc.)
            llm_interface: Optional custom LLM interface
        """
        self.obj = obj
        self.llm_interface = llm_interface  # Can be None
        self.adapter_manager = AdapterManager()
        self.executor = SafeExecutor()
        self.validator = ResponseValidator()
        
        # Get appropriate adapter for the object
        self.adapter = self.adapter_manager.get_adapter(obj)
        if not self.adapter:
            raise ValueError(f"No adapter found for object type: {type(obj)}")
        
        # Initialize query history for context
        self.query_history = []
        
        logger.info(f"AIObject initialized for {type(obj).__name__}")
        if self.llm_interface is None:
            logger.warning("No LLM interface provided - natural language queries will not be available")
    
    def ask(self, query: str, **kwargs) -> Any:
        """
        Process natural language query and return result.
        
        Args:
            query: Natural language question/request
            **kwargs: Additional parameters for LLM or execution
            
        Returns:
            Result of executing the generated code
        """
        if self.llm_interface is None:
            raise ValueError("No LLM interface available. Please provide an LLM interface to use natural language queries.")
        
        try:
            # Get object metadata from adapter
            metadata = self.adapter.get_metadata(self.obj)
            
            # Build context for LLM
            context = self._build_context(metadata, query)
            
            # Generate code using LLM
            llm_response = self.llm_interface.generate_code(
                query=query,
                context=context,
                **kwargs
            )
            
            # Validate LLM response format
            if not self.validator.validate_response(llm_response):
                raise ValueError("Invalid LLM response format")
            
            # Parse response
            response_data = json.loads(llm_response)
            code = self._extract_code(response_data.get("code", ""))
            
            # Execute code safely
            result = self.executor.execute(
                code=code,
                context_vars={"obj": self.obj, "df": self.obj}  # Support common variable names
            )
            
            # Store in history
            self.query_history.append({
                "query": query,
                "code": code,
                "result_type": type(result).__name__,
                "explanation": response_data.get("explanation", "")
            })
            
            logger.info(f"Query executed successfully: {query[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
            raise
    
    def optimize(self, strategy: str = "memory") -> Dict[str, Any]:
        """
        Apply AI-driven optimizations to the object.
        
        Args:
            strategy: Optimization strategy ("memory", "performance", "auto")
            
        Returns:
            Dictionary with optimization results
        """
        if not hasattr(self.adapter, 'optimize'):
            return {"message": "Optimization not supported for this object type"}
        
        return self.adapter.optimize(self.obj, strategy=strategy)
    
    def visualize(self, request: str, **kwargs) -> Any:
        """
        Generate AI-driven visualizations.
        
        Args:
            request: Natural language description of desired visualization
            **kwargs: Additional parameters for visualization
            
        Returns:
            Matplotlib/Plotly figure or display object
        """
        viz_query = f"Create a visualization: {request}"
        return self.ask(viz_query, **kwargs)
    
    def explain(self) -> str:
        """
        Get AI-generated explanation of the object structure and content.
        
        Returns:
            Human-readable explanation of the object
        """
        if self.llm_interface is None:
            # Return basic explanation without AI
            metadata = self.adapter.get_metadata(self.obj)
            return f"Object type: {metadata.get('type', 'Unknown')}\nMetadata: {metadata}"
        
        metadata = self.adapter.get_metadata(self.obj)
        return self.llm_interface.explain_object(metadata)
    
    def get_history(self) -> list:
        """
        Get query execution history.
        
        Returns:
            List of previous queries and their results
        """
        return self.query_history.copy()
    
    def clear_history(self):
        """Clear query execution history."""
        self.query_history.clear()
        logger.info("Query history cleared")
    
    def _build_context(self, metadata: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Build context dictionary for LLM prompt."""
        context = {
            "object_type": metadata.get("type", "Unknown"),
            "object_metadata": metadata,
            "previous_queries": self.query_history[-3:],  # Last 3 queries for context
            "current_query": query
        }
        return context
    
    def _extract_code(self, code_block: str) -> str:
        """Extract Python code from markdown code block."""
        if "```python" in code_block:
            # Extract code between ```python and ```
            start = code_block.find("```python") + 9
            end = code_block.find("```", start)
            return code_block[start:end].strip()
        elif "```" in code_block:
            # Extract code between ``` and ```
            start = code_block.find("```") + 3
            end = code_block.find("```", start)
            return code_block[start:end].strip()
        else:
            return code_block.strip()
    
    def __repr__(self) -> str:
        obj_type = type(self.obj).__name__
        return f"AIObject({obj_type})"
