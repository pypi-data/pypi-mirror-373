"""
Utility functions for the Velatir SDK.
"""
import inspect
from typing import Any, Dict, Callable

def get_function_signature(func: Callable) -> Dict[str, Any]:
    """
    Extract function signature information.
    
    Args:
        func (Callable): The function to analyze
        
    Returns:
        Dict[str, Any]: Dictionary with function signature info
    """
    sig = inspect.signature(func)
    params = {}
    
    for name, param in sig.parameters.items():
        param_info = {
            "name": name,
            "kind": str(param.kind),
        }
        
        if param.default is not param.empty:
            # Handle default values that are not JSON serializable
            if isinstance(param.default, (str, int, float, bool, type(None))):
                param_info["default"] = param.default
            else:
                param_info["default"] = str(param.default)
                
        if param.annotation is not param.empty:
            # Handle annotations that are not JSON serializable
            param_info["annotation"] = str(param.annotation)
            
        params[name] = param_info
        
    return {
        "parameters": params,
        "return_annotation": str(sig.return_annotation) if sig.return_annotation is not sig.empty else None
    }

def get_function_info(func: Callable) -> Dict[str, Any]:
    """
    Get comprehensive information about a function.
    
    Args:
        func (Callable): The function to analyze
        
    Returns:
        Dict[str, Any]: Dictionary with function info
    """
    return {
        "name": func.__name__,
        "module": func.__module__,
        "doc": func.__doc__,
        "signature": get_function_signature(func),
        "is_async": inspect.iscoroutinefunction(func),
    }