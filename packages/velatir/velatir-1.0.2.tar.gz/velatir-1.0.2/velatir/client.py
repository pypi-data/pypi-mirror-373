"""
Client for interacting with the Velatir API.
"""
import asyncio
import logging
import time
import json
from enum import Enum
from typing import Dict, Any, Optional, Union, Callable

import httpx

from .models import VelatirResponse
from .exceptions import VelatirError, VelatirAPIError, VelatirTimeoutError

logger = logging.getLogger("velatir")

class LogLevel(Enum):
    """Log levels for controlling verbosity of Velatir SDK."""
    NONE = 0
    ERROR = 1
    INFO = 2
    DEBUG = 3

class Client:
    """Client for interacting with the Velatir API."""
    
    DEFAULT_BASE_URL = "https://api.velatir.com/api/v1"
    DEFAULT_TIMEOUT = 10.0  # seconds
    
    def __init__(
        self, 
        api_key: str = None, 
        base_url: str = None,
        timeout: float = None,
        log_level: Union[LogLevel, int, None] = LogLevel.ERROR,
        max_retries: int = 3,
        retry_backoff: float = 0.5
    ):
        """
        Initialize the Velatir client.
        
        Args:
            api_key (str, optional): Your Velatir API key
            base_url (str, optional): Custom API base URL
            timeout (float, optional): Request timeout in seconds
            log_level (LogLevel, optional): Logging verbosity level
            max_retries (int, optional): Maximum number of retries for failed requests
            retry_backoff (float, optional): Base backoff time in seconds for retries
        """
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        
        # Handle log_level carefully to avoid ValueError with None
        if log_level is None:
            self.log_level = LogLevel.ERROR
        elif isinstance(log_level, LogLevel):
            self.log_level = log_level
        else:
            try:
                self.log_level = LogLevel(log_level)
            except (ValueError, TypeError):
                self.log_level = LogLevel.ERROR
        
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._client = None
        self._closed = False
    
    def _create_client(self):
        """Create a new HTTP client"""
        return httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "X-API-Key": f"{self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"Velatir-Python/{__import__('velatir').__version__}"
            }
        )

    @property
    def client(self):
        """Get or create the HTTP client"""
        if self._client is None or self._closed:
            self._client = self._create_client()
            self._closed = False
        return self._client

    async def close(self):
        """Close the underlying HTTP client."""
        if self._client is not None and not self._closed:
            await self._client.aclose()
            self._closed = True
            self._client = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _log(self, level: LogLevel, message: str, data: Any = None):
        """
        Log a message at the specified level if the client's log level is high enough.
        
        Args:
            level (LogLevel): The level to log at
            message (str): The message to log
            data (Any, optional): Additional data to log
        """
        if self.log_level.value >= level.value:
            if level == LogLevel.ERROR:
                if data:
                    logger.error("%s - %s", message, json.dumps(data) if not isinstance(data, str) else data)
                else:
                    logger.error(message)
            elif level == LogLevel.INFO:
                if data:
                    logger.info("%s - %s", message, json.dumps(data) if not isinstance(data, str) else data)
                else:
                    logger.info(message)
            elif level == LogLevel.DEBUG:
                if data:
                    logger.debug("%s - %s", message, json.dumps(data) if not isinstance(data, str) else data)
                else:
                    logger.debug(message)
    
    async def _request(
        self, 
        method: str, 
        path: str, 
        params: Dict[str, Any] = None, 
        json: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Velatir API.
        
        Args:
            method (str): HTTP method
            path (str): API endpoint path
            params (Dict[str, Any], optional): Query parameters
            json (Dict[str, Any], optional): JSON body
            
        Returns:
            Dict[str, Any]: API response
            
        Raises:
            VelatirAPIError: If the API returns an error
            VelatirTimeoutError: If the request times out
            VelatirError: For other errors
        """
        url = f"{self.base_url}{path}"
        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                # Log the request
                self._log(LogLevel.INFO, f"Making {method} request to {url}")
                if json:
                    self._log(LogLevel.DEBUG, "Request payload", json)
                if params:
                    self._log(LogLevel.DEBUG, "Request params", params)
                
                # Record start time for request duration logging
                start_time = time.time()
                
                # Make the request
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json
                )
                
                # Calculate request duration
                duration = time.time() - start_time
                self._log(LogLevel.DEBUG, f"Request completed in {duration:.2f}s")
                
                # Handle response
                response.raise_for_status()
                response_json = response.json()
                
                # Log the response
                self._log(LogLevel.INFO, f"Received response from {url} - {response.status_code}")
                self._log(LogLevel.DEBUG, "Response data", response_json)
                
                return response_json
            
            except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                
                # Only retry on certain status codes or network/timeout errors
                should_retry = (
                    isinstance(e, httpx.TimeoutException) or 
                    isinstance(e, httpx.NetworkError) or
                    (isinstance(e, httpx.HTTPStatusError) and e.response.status_code >= 500)
                )
                
                if not should_retry or retries >= self.max_retries:
                    break
                
                # Calculate backoff with exponential increase
                backoff = self.retry_backoff * (2 ** retries)
                retries += 1
                
                self._log(
                    LogLevel.INFO, 
                    f"Request failed, retrying in {backoff:.2f}s ({retries}/{self.max_retries})",
                    str(e)
                )
                
                await asyncio.sleep(backoff)
                continue
            
            except Exception as e:
                last_error = e
                self._log(LogLevel.ERROR, "Unexpected error during request", str(e))
                break
        
        # If we've exhausted retries or hit a non-retryable error, raise the appropriate exception
        if isinstance(last_error, httpx.HTTPStatusError):
            try:
                error_data = last_error.response.json()
                message = error_data.get("message", str(last_error))
                code = error_data.get("code", last_error.response.status_code)
            except Exception:
                message = str(last_error)
                code = last_error.response.status_code
            
            self._log(LogLevel.ERROR, f"API error: {message}", error_data)
            
            raise VelatirAPIError(
                message=message,
                code=code,
                http_status=last_error.response.status_code,
                http_body=last_error.response.text
            )
        
        elif isinstance(last_error, httpx.TimeoutException):
            self._log(LogLevel.ERROR, "Request timed out", str(last_error))
            raise VelatirTimeoutError(f"Request timed out after {self.max_retries} retries: {str(last_error)}")
        
        else:
            self._log(LogLevel.ERROR, "Communication error", str(last_error) if last_error else "Unknown error")
            raise VelatirError(f"Error communicating with Velatir API: {str(last_error)}")
    
    async def create_review_task(
        self,
        function_name: str,
        args: Dict[str, Any],
        doc: Optional[str] = None,
        llm_explanation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_review_task_id: Optional[str] = None
    ) -> VelatirResponse:
        """
        Create a review task for a function call.
        
        Args:
            function_name (str): Name of the function being reviewed
            args (Dict[str, Any]): Arguments passed to the function
            doc (str, optional): Function docstring
            llm_explanation (str, optional): LLM explanation of the request
            metadata (Dict[str, Any], optional): Additional metadata
            parent_review_task_id (str, optional): ID of parent review task
            
        Returns:
            VelatirResponse: API response with review_task_id and state
        """
        payload = {
            "functionName": function_name,
            "args": args,
            "doc": doc,
            "llmExplanation": llm_explanation,
            "metadata": metadata or {},
            "parentReviewTaskId": parent_review_task_id
        }
        
        response = await self._request("POST", "/review-tasks", json=payload)
        return VelatirResponse(**response)
    
    async def get_review_task_status(self, review_task_id: str) -> VelatirResponse:
        """
        Get the status of a review task.
        
        Args:
            review_task_id (str): The ID of the review task to check
            
        Returns:
            VelatirResponse: API response with review_task_id and state
        """
        response = await self._request("GET", f"/review-tasks/{review_task_id}")
        return VelatirResponse(**response)
    
    async def wait_for_approval(
        self, 
        review_task_id: str, 
        polling_interval: float = 5.0,
        max_attempts: int = None
    ) -> VelatirResponse:
        """
        Wait for a review task to be approved or denied.
        
        Args:
            review_task_id (str): The ID of the review task to check
            polling_interval (float, optional): Seconds between polling attempts
            max_attempts (int, optional): Maximum number of polling attempts
            
        Returns:
            VelatirResponse: API response with review_task_id and state
            
        Raises:
            VelatirTimeoutError: If max_attempts is reached
        """
        attempts = 0
        
        self._log(LogLevel.INFO, f"Waiting for approval of review task {review_task_id}")
        
        while True:
            if max_attempts and attempts >= max_attempts:
                error_msg = f"Max polling attempts ({max_attempts}) reached waiting for review task {review_task_id}"
                self._log(LogLevel.ERROR, error_msg)
                raise VelatirTimeoutError(error_msg)
                
            response = await self.get_review_task_status(review_task_id)
            
            if not response.is_pending:
                self._log(
                    LogLevel.INFO, 
                    f"Review task {review_task_id} {response.state}",
                    {"state": response.state, "requested_change": response.requested_change}
                )
                return response
            
            attempts += 1
            self._log(
                LogLevel.DEBUG, 
                f"Review task {review_task_id} still pending, attempt {attempts}" + 
                (f"/{max_attempts}" if max_attempts else ""),
                {"attempt": attempts, "max_attempts": max_attempts}
            )
                
            await asyncio.sleep(polling_interval)
            
    # Synchronous client methods
    def create_review_task_sync(
        self,
        function_name: str,
        args: Dict[str, Any],
        doc: Optional[str] = None,
        llm_explanation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_review_task_id: Optional[str] = None
    ) -> VelatirResponse:
        """
        Synchronous version of create_review_task.
        
        Args:
            function_name (str): Name of the function being reviewed
            args (Dict[str, Any]): Arguments passed to the function
            doc (str, optional): Function docstring
            llm_explanation (str, optional): LLM explanation of the request
            metadata (Dict[str, Any], optional): Additional metadata
            parent_review_task_id (str, optional): ID of parent review task
            
        Returns:
            VelatirResponse: API response with review_task_id and state
        """
        return asyncio.run(self.create_review_task(
            function_name=function_name,
            args=args,
            doc=doc,
            llm_explanation=llm_explanation,
            metadata=metadata,
            parent_review_task_id=parent_review_task_id
        ))
    
    def get_review_task_status_sync(self, review_task_id: str) -> VelatirResponse:
        """
        Synchronous version of get_review_task_status.
        
        Args:
            review_task_id (str): The ID of the review task to check
            
        Returns:
            VelatirResponse: API response with review_task_id and state
        """
        return asyncio.run(self.get_review_task_status(review_task_id))
    
    def wait_for_approval_sync(
        self, 
        review_task_id: str, 
        polling_interval: float = 5.0,
        max_attempts: int = None
    ) -> VelatirResponse:
        """
        Synchronous version of wait_for_approval.
        
        Args:
            review_task_id (str): The ID of the review task to check
            polling_interval (float, optional): Seconds between polling attempts
            max_attempts (int, optional): Maximum number of polling attempts
            
        Returns:
            VelatirResponse: API response with review_task_id and state
            
        Raises:
            VelatirTimeoutError: If max_attempts is reached
        """
        return asyncio.run(self.wait_for_approval(
            review_task_id=review_task_id,
            polling_interval=polling_interval,
            max_attempts=max_attempts
        ))