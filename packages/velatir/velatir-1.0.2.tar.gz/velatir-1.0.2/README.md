# velatir

[![PyPI version](https://badge.fury.io/py/velatir.svg)](https://badge.fury.io/py/velatir)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [Velatir](https://velatir.com), a service that allows you to monitor and approve/reject AI function calls through review tasks.

## Installation

```bash
pip install velatir
```

## Quick Start

```python
import velatir

# Initialize the SDK with your API key
velatir.init(api_key="your-api-key")

# Decorate functions you want to monitor
@velatir.review_task()
async def send_email(to: str, subject: str, body: str):
    """Send an email to the customer"""
    print(f"Sending email to {to}: {subject}")
    # Your email sending logic here
    
# Call the function as usual (or from LLM tool)
await send_email("customer@example.com", "Welcome!", "Hello from Velatir!")
```

## How It Works

The `@review_task()` decorator intercepts function calls and:

1. Creates a review task with function details and arguments via the Velatir API
2. Processes the API response:
   - If `approved`: The function runs immediately
   - If `pending`: The SDK polls the API every 5 seconds until approved or denied
   - If `denied`: An exception is raised and the function doesn't run

## Features

- Monitor function calls in real-time through review tasks
- Approve or reject function execution with optional feedback
- Automatically handle pending approval states
- Works with both synchronous and asynchronous functions
- Configurable polling intervals and timeout settings
- Review task chaining via parent task IDs
- LLM explanation support for better context

## Advanced Usage

### Custom Polling Configuration

```python
@velatir.review_task(polling_interval=2.0, max_attempts=30)
async def delete_user(user_id: str):
    """Delete a user from the system"""
    # Deletion logic here
```

### Adding Metadata

```python
@velatir.review_task(metadata={"priority": "high", "team": "billing"})
async def charge_credit_card(card_id: str, amount: float):
    """Charge a customer's credit card"""
    # Charging logic here
```

### Direct Client Usage

You can also use the client directly for more control:

```python
# Get the global client
client = velatir.get_client()

# Create a review task synchronously
response = client.create_review_task_sync(
    function_name="charge_card",
    args={"card_id": "card_123", "amount": 99.99},
    doc="Charge customer credit card",
    llm_explanation="LLM is requesting to charge the customer",
    metadata={"priority": "high"}
)

# Wait for approval synchronously
if response.is_pending:
    approval = client.wait_for_approval_sync(
        review_task_id=response.review_task_id,
        polling_interval=2.0
    )
```

### Asynchronous Client Usage

```python
async with velatir.Client(api_key="your-api-key") as client:
    # Create a review task
    response = await client.create_review_task(
        function_name="send_email",
        args={"to": "user@example.com", "subject": "Hello"},
        doc="Send email to user",
        llm_explanation="AI is sending a welcome email",
        metadata={"priority": "low"}
    )
    
    # Wait for approval if pending
    if response.is_pending:
        approval = await client.wait_for_approval(
            review_task_id=response.review_task_id,
            polling_interval=5.0
        )
```

### Configuration

Configure logging and retries:

```python
import velatir
from velatir import LogLevel

velatir.init(
    api_key="your-api-key",
    log_level=LogLevel.INFO,  # 0=NONE, 1=ERROR, 2=INFO, 3=DEBUG
    max_retries=3,
    retry_backoff=0.5
)

# Configure Python's logging for Velatir
import logging
velatir.configure_logging(level=logging.INFO)
```

## Error Handling

When a review task is denied:

```python
try:
    await risky_function()
except velatir.VelatirReviewTaskDeniedError as e:
    print(f"Review task denied: {e}")
    print(f"Review Task ID: {e.review_task_id}")
    print(f"Requested Change: {e.requested_change}")
```

### Available Error Types

```python
# Base error class
velatir.VelatirError

# API-specific errors
velatir.VelatirAPIError                # API returned an error
velatir.VelatirTimeoutError            # Request timed out
velatir.VelatirReviewTaskDeniedError   # Review task execution denied
```

## API Reference

### Client Methods

#### Async Methods
- `create_review_task(function_name, args, doc=None, llm_explanation=None, metadata=None, parent_review_task_id=None)` - Create a new review task
- `get_review_task_status(review_task_id)` - Get the status of a review task
- `wait_for_approval(review_task_id, polling_interval=5.0, max_attempts=None)` - Wait for approval

#### Sync Methods
- `create_review_task_sync(...)` - Synchronous version of `create_review_task`
- `get_review_task_status_sync(review_task_id)` - Synchronous version of `get_review_task_status`
- `wait_for_approval_sync(...)` - Synchronous version of `wait_for_approval`

### Response Properties

- `review_task_id: str` - Unique identifier for the review task
- `state: str` - Current state ('approved', 'denied', or 'pending')
- `requested_change: Optional[str]` - Optional feedback when denied
- `is_approved: bool` - Helper property
- `is_denied: bool` - Helper property  
- `is_pending: bool` - Helper property

### Configuration Options

```python
velatir.init(
    api_key="your-api-key",           # Your Velatir API key
    base_url="https://api.velatir.com/api/v1",  # Custom API base URL
    log_level=LogLevel.ERROR,         # Logging verbosity level
    max_retries=3,                    # Maximum number of retries
    retry_backoff=0.5                 # Base backoff time in seconds
)
```

### Decorator Options

```python
@velatir.review_task(
    polling_interval=5.0,    # Seconds between polling attempts
    max_attempts=None,       # Maximum number of polling attempts
    metadata={}              # Additional metadata to send
)
```

## Working with Sync Functions

The decorator works seamlessly with both sync and async functions:

```python
@velatir.review_task()
def sync_function(param: str):
    """A synchronous function"""
    print(f"Processing: {param}")
    return f"Result: {param}"

# This will work even though the function is sync
result = sync_function("test")
```

## Python Version Support

- Python 3.7+
- Full async/await support
- Type hints included

## Development

### Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/
```

### Building the Package

```bash
pip install build
python -m build
```

## Documentation

For more detailed documentation, visit [https://www.velatir.com/docs](https://www.velatir.com/docs)

## License

MIT - see [LICENSE](../../LICENSE) file for details.

## Support

- 🐛 [Report bugs](https://github.com/velatir/velatir-sdk/issues)
- 💬 [Get help](https://www.velatir.com/docs)
- 📧 [Contact support](mailto:hello@velatir.com)