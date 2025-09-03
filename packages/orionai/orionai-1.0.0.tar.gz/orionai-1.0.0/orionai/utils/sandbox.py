"""
Safe Code Execution Sandbox for OrionAI
=======================================

Provides secure execution environment for LLM-generated code.
"""

import ast
import logging
import sys
import traceback
from io import StringIO
from typing import Any, Dict, List, Optional, Set
import contextlib

logger = logging.getLogger(__name__)


class CodeValidator:
    """Validates generated code for security and safety."""
    
    # Dangerous modules and functions to block
    BLOCKED_MODULES = {
        'os', 'sys', 'subprocess', 'shutil', 'pathlib', 'glob',
        'socket', 'urllib', 'requests', 'http', 'ftplib', 'smtplib',
        '__builtin__', '__builtins__', 'builtins',
        'importlib', 'pkgutil', 'imp'
    }
    
    BLOCKED_FUNCTIONS = {
        'exec', 'eval', 'compile', 'open', '__import__',
        'getattr', 'setattr', 'delattr', 'hasattr',
        'globals', 'locals', 'vars', 'dir'
    }
    
    BLOCKED_ATTRIBUTES = {
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__globals__', '__code__', '__func__', '__self__'
    }
    
    def __init__(self):
        self.errors = []
    
    def validate(self, code: str) -> bool:
        """
        Validate code for security issues.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if code is safe, False otherwise
        """
        self.errors = []
        
        try:
            tree = ast.parse(code)
            self._check_ast_node(tree)
            return len(self.errors) == 0
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Validation error: {str(e)}")
            return False
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()
    
    def _check_ast_node(self, node: ast.AST):
        """Recursively check AST nodes for dangerous patterns."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.BLOCKED_MODULES:
                    self.errors.append(f"Blocked import: {alias.name}")
        
        elif isinstance(node, ast.ImportFrom):
            if node.module in self.BLOCKED_MODULES:
                self.errors.append(f"Blocked import from: {node.module}")
        
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.BLOCKED_FUNCTIONS:
                    self.errors.append(f"Blocked function call: {node.func.id}")
        
        elif isinstance(node, ast.Attribute):
            if node.attr in self.BLOCKED_ATTRIBUTES:
                self.errors.append(f"Blocked attribute access: {node.attr}")
        
        # Recursively check child nodes
        for child in ast.iter_child_nodes(node):
            self._check_ast_node(child)


class SafeExecutor:
    """
    Safe execution environment for generated Python code.
    """
    
    def __init__(self, timeout: float = 30.0):
        """
        Initialize safe executor.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
        self.validator = CodeValidator()
        self._setup_safe_builtins()
    
    def execute(self, code: str, context_vars: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute code safely in restricted environment.
        
        Args:
            code: Python code to execute
            context_vars: Variables to make available in execution context
            
        Returns:
            Result of code execution
            
        Raises:
            SecurityError: If code contains dangerous operations
            TimeoutError: If execution takes too long
            RuntimeError: If execution fails
        """
        # Validate code first
        if not self.validator.validate(code):
            errors = self.validator.get_errors()
            raise SecurityError(f"Code validation failed: {'; '.join(errors)}")
        
        # Prepare execution context
        exec_globals = self._create_safe_globals()
        if context_vars:
            exec_globals.update(context_vars)
        
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Execute code with timeout
            result = self._execute_with_timeout(code, exec_globals)
            
            # Capture any printed output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            if stderr_output:
                logger.warning(f"Code execution produced stderr: {stderr_output}")
            
            # Return result or stdout if no explicit result
            if result is None and stdout_output:
                return stdout_output.strip()
            
            return result
            
        except Exception as e:
            stderr_output = stderr_capture.getvalue()
            error_msg = f"Execution failed: {str(e)}"
            if stderr_output:
                error_msg += f"\\nStderr: {stderr_output}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _execute_with_timeout(self, code: str, exec_globals: Dict[str, Any]) -> Any:
        """Execute code with timeout (simplified version)."""
        # For now, we'll use basic execution
        # In production, consider using threading or subprocess with timeout
        
        try:
            # Compile code
            compiled_code = compile(code, '<string>', 'exec')
            
            # Execute
            exec_locals = {}
            exec(compiled_code, exec_globals, exec_locals)
            
            # Try to find result
            # Look for common result variable names
            for var_name in ['result', '_', 'output', 'ans', 'answer']:
                if var_name in exec_locals:
                    return exec_locals[var_name]
            
            # If no explicit result variable, return the last expression value
            # This is a simplified approach - in practice you'd need more sophisticated AST analysis
            return None
            
        except Exception as e:
            # Re-raise with more context
            tb = traceback.format_exc()
            logger.debug(f"Code execution traceback: {tb}")
            raise
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create safe global environment for code execution."""
        safe_globals = {
            '__builtins__': self.safe_builtins,
            # Common safe modules that might be needed
            'pd': None,  # Will be set to pandas if available
            'np': None,  # Will be set to numpy if available
            'plt': None, # Will be set to matplotlib.pyplot if available
        }
        
        # Add safe modules if available
        try:
            import pandas as pd
            safe_globals['pd'] = pd
        except ImportError:
            pass
        
        try:
            import numpy as np
            safe_globals['np'] = np
        except ImportError:
            pass
        
        try:
            import matplotlib.pyplot as plt
            safe_globals['plt'] = plt
        except ImportError:
            pass
        
        return safe_globals
    
    def _setup_safe_builtins(self):
        """Setup safe builtin functions."""
        # Start with minimal safe builtins
        self.safe_builtins = {
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'dict': dict,
            'enumerate': enumerate,
            'filter': filter,
            'float': float,
            'int': int,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'range': range,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'type': type,
            'zip': zip,
            # Math functions
            'pow': pow,
            # String methods are generally safe
            'print': print,  # Allow print for debugging
        }


class SecurityError(Exception):
    """Raised when code contains security violations."""
    pass
