"""
Response Validator for OrionAI
==============================

Validates LLM responses to ensure they follow the expected format.
"""

import json
import logging
import re
import ast
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class CodeValidator:
    """Validates generated Python code for safety."""
    
    def __init__(self):
        self.forbidden_modules = {
            'os', 'subprocess', 'sys', 'eval', 'exec', 'open', '__import__',
            'compile', 'globals', 'locals', 'vars', 'dir', 'getattr', 'setattr',
            'delattr', 'hasattr', 'input', 'raw_input'
        }
        
        self.forbidden_builtins = {
            'eval', 'exec', 'compile', '__import__', 'open', 'input', 'raw_input'
        }
        
        self.allowed_pandas_methods = {
            'head', 'tail', 'describe', 'info', 'shape', 'columns', 'dtypes',
            'mean', 'sum', 'count', 'min', 'max', 'std', 'var', 'median',
            'groupby', 'sort_values', 'sort_index', 'reset_index', 'set_index',
            'drop', 'dropna', 'fillna', 'query', 'loc', 'iloc', 'at', 'iat',
            'unique', 'nunique', 'value_counts', 'sample', 'nlargest', 'nsmallest'
        }
    
    def is_safe(self, code: str) -> bool:
        """
        Check if code is safe to execute.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if code is safe, False otherwise
        """
        try:
            # Parse the code to AST
            tree = ast.parse(code)
            
            # Check for forbidden operations
            for node in ast.walk(tree):
                if not self._is_node_safe(node):
                    return False
            
            return True
            
        except SyntaxError:
            logger.warning("Code has syntax errors")
            return False
        except Exception as e:
            logger.error(f"Code validation error: {e}")
            return False
    
    def _is_node_safe(self, node: ast.AST) -> bool:
        """Check if an AST node is safe."""
        
        # Check for imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return self._is_import_safe(node)
        
        # Check for function calls
        if isinstance(node, ast.Call):
            return self._is_call_safe(node)
        
        # Check for attribute access
        if isinstance(node, ast.Attribute):
            return self._is_attribute_safe(node)
        
        return True
    
    def _is_import_safe(self, node: ast.AST) -> bool:
        """Check if import is safe."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.forbidden_modules:
                    return False
        
        elif isinstance(node, ast.ImportFrom):
            if node.module in self.forbidden_modules:
                return False
        
        return True
    
    def _is_call_safe(self, node: ast.Call) -> bool:
        """Check if function call is safe."""
        # Get function name
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        
        if func_name in self.forbidden_builtins:
            return False
        
        return True
    
    def _is_attribute_safe(self, node: ast.Attribute) -> bool:
        """Check if attribute access is safe."""
        # For now, allow all attribute access
        # Could be more restrictive in the future
        return True


class ResponseValidator:
    """Validates LLM responses for format and content safety."""
    
    def __init__(self):
        self.required_fields = {"explanation", "code", "expected_output"}
    
    def validate_response(self, response: str) -> bool:
        """
        Validate LLM response format and content.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            True if response is valid, False otherwise
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)
            
            # Check required fields
            if not self._has_required_fields(data):
                logger.warning("Response missing required fields")
                return False
            
            # Validate code format
            if not self._validate_code_format(data.get("code", "")):
                logger.warning("Invalid code format in response")
                return False
            
            # Check for reasonable content lengths
            if not self._validate_content_length(data):
                logger.warning("Response content length validation failed")
                return False
            
            return True
            
        except json.JSONDecodeError:
            logger.warning("Response is not valid JSON")
            return False
        except Exception as e:
            logger.error(f"Response validation error: {str(e)}")
            return False
    
    def extract_and_validate(self, response: str) -> Dict[str, Any]:
        """
        Extract and validate response data.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Dictionary with extracted data or error information
        """
        try:
            data = json.loads(response)
            
            if self.validate_response(response):
                return {
                    "valid": True,
                    "data": data
                }
            else:
                return {
                    "valid": False,
                    "error": "Validation failed",
                    "data": data
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "data": {}
            }
    
    def _has_required_fields(self, data: Dict[str, Any]) -> bool:
        """Check if response has all required fields."""
        return all(field in data for field in self.required_fields)
    
    def _validate_code_format(self, code: str) -> bool:
        """
        Validate that code is properly formatted.
        
        Args:
            code: Code string to validate
            
        Returns:
            True if code format is valid
        """
        if not code or not isinstance(code, str):
            return False
        
        # Check for code block markers
        if "```python" in code or "```" in code:
            # Extract code between markers
            if "```python" in code:
                pattern = r"```python\s*(.*?)\s*```"
            else:
                pattern = r"```\s*(.*?)\s*```"
            
            matches = re.findall(pattern, code, re.DOTALL)
            if not matches:
                return False
            
            actual_code = matches[0].strip()
        else:
            actual_code = code.strip()
        
        # Basic validation - should not be empty
        if not actual_code:
            return False
        
        # Should look like Python code (very basic check)
        python_keywords = [
            'def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except',
            'import', 'from', 'return', 'yield', 'with', 'as', 'lambda', 'and', 'or',
            'not', 'in', 'is', 'True', 'False', 'None', '=', '+', '-', '*', '/', '%'
        ]
        
        # Check if code contains some Python-like elements
        has_python_elements = any(keyword in actual_code for keyword in python_keywords)
        
        # Also check for common pandas/dataframe patterns
        dataframe_patterns = ['.groupby', '.mean()', '.sum()', '.head()', '.tail()', '.describe()']
        has_dataframe_patterns = any(pattern in actual_code for pattern in dataframe_patterns)
        
        return has_python_elements or has_dataframe_patterns
    
    def _validate_content_length(self, data: Dict[str, Any]) -> bool:
        """
        Validate content lengths are reasonable.
        
        Args:
            data: Response data dictionary
            
        Returns:
            True if content lengths are reasonable
        """
        explanation = data.get("explanation", "")
        code = data.get("code", "")
        expected_output = data.get("expected_output", "")
        
        # Basic length checks
        if len(explanation) > 1000:  # Explanation too long
            return False
        
        if len(code) > 5000:  # Code too long
            return False
        
        if len(expected_output) > 1000:  # Expected output description too long
            return False
        
        # Minimum length checks
        if len(explanation.strip()) < 5:  # Explanation too short
            return False
        
        if len(code.strip()) < 3:  # Code too short
            return False
        
        return True
    
    def sanitize_response(self, response: str) -> str:
        """
        Attempt to sanitize and fix common response issues.
        
        Args:
            response: Raw response string
            
        Returns:
            Sanitized response string
        """
        try:
            # Try to extract JSON from response if it's embedded in other text
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response, re.DOTALL)
            
            if match:
                json_str = match.group(0)
                # Try to parse to validate
                json.loads(json_str)
                return json_str
            
            return response
            
        except Exception:
            return response
