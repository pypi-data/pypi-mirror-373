"""
Velatir SDK for monitoring and approval of AI function calls.
"""
__version__ = "1.0.2"

# Global client instance
_client = None

def init(api_key=None, base_url=None, log_level=None, max_retries=3, retry_backoff=0.5):
    """
    Initialize the Velatir client with your API key.
    
    Args:
        api_key (str): Your Velatir API key
        base_url (str, optional): Custom API base URL
        log_level (LogLevel, optional): Logging verbosity level (0=NONE, 1=ERROR, 2=INFO, 3=DEBUG)
        max_retries (int, optional): Maximum number of retries for failed requests
        retry_backoff (float, optional): Base backoff time in seconds for retries
    
    Returns:
        Client: The initialized client instance
    
    Example:
        >>> import velatir
        >>> velatir.init(api_key="your-api-key", log_level=2)  # INFO level logging
    """
    from .client import Client, LogLevel
    global _client
    
    # No need to handle log_level here, as the Client class now handles it internally
    
    _client = Client(
        api_key=api_key, 
        base_url=base_url, 
        log_level=log_level, 
        max_retries=max_retries,
        retry_backoff=retry_backoff
    )
    return _client

def get_client():
    """Get the global client instance."""
    global _client
    if _client is None:
        raise RuntimeError("Velatir client is not initialized. Call velatir.init() first.")
    return _client

# Import public API - do this at the end to avoid circular imports
from .decorators import review_task
from .client import Client, LogLevel
from .exceptions import VelatirError, VelatirAPIError, VelatirTimeoutError, VelatirReviewTaskDeniedError

# Set up logging configuration
import logging

def configure_logging(level=None):
    """
    Configure the Velatir logger with the specified log level.
    
    Args:
        level (int, optional): The logging level to use
            (logging.DEBUG, logging.INFO, logging.ERROR, etc.)
    """
    logger = logging.getLogger("velatir")
    
    if level is not None:
        logger.setLevel(level)
    
    # Only add handler if none exist to prevent duplicate logs
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

