"""
Exceptions for the Velatir SDK.
"""

class VelatirError(Exception):
    """Base exception for all Velatir errors."""
    pass

class VelatirAPIError(VelatirError):
    """Exception raised when the Velatir API returns an error."""
    
    def __init__(
        self, 
        message: str, 
        code: str = None, 
        http_status: int = None, 
        http_body: str = None
    ):
        self.message = message
        self.code = code
        self.http_status = http_status
        self.http_body = http_body
        super().__init__(self.message)

class VelatirTimeoutError(VelatirError):
    """Exception raised when a request times out."""
    pass

class VelatirReviewTaskDeniedError(VelatirError):
    """Exception raised when a review task is denied."""
    
    def __init__(self, review_task_id: str, requested_change: str = None):
        self.review_task_id = review_task_id
        self.requested_change = requested_change
        message = f"Function execution denied by Velatir (review_task_id: {review_task_id})"
        if requested_change:
            message += f" - {requested_change}"
        super().__init__(message)