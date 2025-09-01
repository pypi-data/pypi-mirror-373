"""
Decorators for monitoring functions with Velatir.
"""
import asyncio
import inspect
import functools
from typing import Callable, Any, Dict, Optional, TypeVar, cast

# Import from exceptions directly to avoid circular imports
from .exceptions import VelatirReviewTaskDeniedError

F = TypeVar('F', bound=Callable[..., Any])

def review_task(
    polling_interval: float = 5.0,
    max_attempts: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Callable[[F], F]:
    """
    Decorator that creates a review task for a function call through Velatir.
    
    Args:
        polling_interval (float, optional): Seconds between polling attempts
        max_attempts (int, optional): Maximum number of polling attempts
        metadata (Dict[str, Any], optional): Additional metadata to send with request
        
    Returns:
        Callable: Decorated function
        
    Example:
        @velatir.review_task()
        async def send_email(to: str, subject: str, body: str):
            print(f"Sending email to {to}: {subject}")
    """
    def decorator(func: F) -> F:
        is_async = inspect.iscoroutinefunction(func)
        
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Import get_client here to avoid circular imports
            from . import get_client
            
            client = get_client()
            try:
                # Get function information
                func_name = func.__name__
                doc = func.__doc__
                
                # Prepare arguments
                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Convert args to a serializable dictionary
                args_dict = {}
                for k, v in bound_args.arguments.items():
                    # Handle special data types by converting them to strings
                    if isinstance(v, (str, int, float, bool, type(None), list, dict)):
                        # Common serializable types that can be sent directly
                        args_dict[k] = v
                    else:
                        # For other types, convert to string representation
                        try:
                            # Try to convert to dict if the object has a to_dict method
                            if hasattr(v, "to_dict") and callable(getattr(v, "to_dict")):
                                args_dict[k] = v.to_dict()
                            # Try to convert to dict if the object has a dict method (like dataclasses)
                            elif hasattr(v, "__dict__"):
                                args_dict[k] = v.__dict__
                            else:
                                # Fall back to string representation
                                args_dict[k] = str(v)
                        except Exception:
                            # If all else fails, use string representation
                            args_dict[k] = str(v)
                
                # Create review task
                response = await client.create_review_task(
                    function_name=func_name,
                    args=args_dict,
                    doc=doc,
                    metadata=metadata
                )
                
                # Handle different states
                if response.is_approved:
                    if is_async:
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                elif response.is_pending:
                    approval = await client.wait_for_approval(
                        review_task_id=response.review_task_id,
                        polling_interval=polling_interval,
                        max_attempts=max_attempts
                    )
                    
                    if approval.is_approved:
                        if is_async:
                            return await func(*args, **kwargs)
                        else:
                            return func(*args, **kwargs)
                    else:
                        raise VelatirReviewTaskDeniedError(review_task_id=approval.review_task_id, requested_change=approval.requested_change)
                else:
                    raise VelatirReviewTaskDeniedError(review_task_id=response.review_task_id, requested_change=response.requested_change)
            finally:
                await client.close()
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Always create a new event loop for sync functions
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        # Choose the appropriate wrapper based on whether the original function is async
        if is_async:
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)
            
    return decorator