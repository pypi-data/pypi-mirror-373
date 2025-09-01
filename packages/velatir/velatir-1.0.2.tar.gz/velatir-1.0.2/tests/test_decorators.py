import asyncio
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from velatir.models import VelatirResponse
from velatir.decorators import review_task
from velatir.exceptions import VelatirReviewTaskDeniedError

# Sample functions to be decorated
async def sample_async_function(param1, param2="default"):
    """This is a sample async function"""
    return f"{param1}-{param2}"

def sample_sync_function(param1, param2="default"):
    """This is a sample sync function"""
    return f"{param1}-{param2}"

@pytest.fixture
def mock_client():
    """Fixture to create a mock client and patch get_client()"""
    client = AsyncMock()
    with patch('velatir.get_client', return_value=client):
        yield client

class TestReviewTaskDecorator:
    
    async def test_async_function_approved_immediately(self, mock_client):
        """Test that an async function runs when immediately approved"""
        # Configure mock response
        response = VelatirResponse(
            review_task_id="test-review-task-id",
            state="Approved"
        )
        mock_client.create_review_task.return_value = response
        
        # Apply decorator
        decorated = review_task()(sample_async_function)
        
        # Call function
        result = await decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.create_review_task.assert_called_once()
        mock_client.wait_for_approval.assert_not_called()
    
    async def test_async_function_pending_then_approved(self, mock_client):
        """Test that an async function waits when pending, then runs when approved"""
        # Configure mock responses
        pending_response = VelatirResponse(
            review_task_id="test-review-task-id",
            state="Pending"
        )
        approved_response = VelatirResponse(
            review_task_id="test-review-task-id",
            state="Approved"
        )
        mock_client.create_review_task.return_value = pending_response
        mock_client.wait_for_approval.return_value = approved_response
        
        # Apply decorator
        decorated = review_task()(sample_async_function)
        
        # Call function
        result = await decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.create_review_task.assert_called_once()
        mock_client.wait_for_approval.assert_called_once_with(
            review_task_id="test-review-task-id",
            polling_interval=5.0,
            max_attempts=None
        )
    
    async def test_async_function_denied_immediately(self, mock_client):
        """Test that an async function raises exception when denied immediately"""
        # Configure mock response
        response = VelatirResponse(
            review_task_id="test-review-task-id",
            state="Rejected",
            requested_change="Please provide more details"
        )
        mock_client.create_review_task.return_value = response
        
        # Apply decorator
        decorated = review_task()(sample_async_function)
        
        # Call function and expect exception
        with pytest.raises(VelatirReviewTaskDeniedError) as excinfo:
            await decorated("value1", "value2")
        
        # Verify results
        assert "test-review-task-id" in str(excinfo.value)
        mock_client.create_review_task.assert_called_once()
        mock_client.wait_for_approval.assert_not_called()
    
    def test_sync_function_approved(self, mock_client):
        """Test that a sync function runs when approved"""
        # Configure mock response
        response = VelatirResponse(
            review_task_id="test-review-task-id", 
            state="Approved"
        )
        mock_client.create_review_task.return_value = response
        
        # Apply decorator
        decorated = review_task()(sample_sync_function)
        
        # Call function
        result = decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.create_review_task.assert_called_once()
    
    async def test_metadata_passed_to_client(self, mock_client):
        """Test that metadata is passed to the client correctly"""
        # Configure mock response
        response = VelatirResponse(
            review_task_id="test-review-task-id",
            state="Approved"
        )
        mock_client.create_review_task.return_value = response
        
        # Apply decorator with metadata
        metadata = {"priority": "high", "category": "financial"}
        decorated = review_task(metadata=metadata)(sample_async_function)
        
        # Call function
        result = await decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.create_review_task.assert_called_once()
        call_args = mock_client.create_review_task.call_args
        assert call_args.kwargs["metadata"] == metadata
    
    async def test_polling_configuration(self, mock_client):
        """Test that polling configuration is passed correctly"""
        # Configure mock responses
        pending_response = VelatirResponse(
            review_task_id="test-review-task-id",
            state="Pending"
        )
        approved_response = VelatirResponse(
            review_task_id="test-review-task-id",
            state="Approved"
        )
        mock_client.create_review_task.return_value = pending_response
        mock_client.wait_for_approval.return_value = approved_response
        
        # Apply decorator with custom polling options
        decorated = review_task(
            polling_interval=2.0,
            max_attempts=10
        )(sample_async_function)
        
        # Call function
        result = await decorated("value1", "value2")
        
        # Verify results
        assert result == "value1-value2"
        mock_client.wait_for_approval.assert_called_once_with(
            review_task_id="test-review-task-id",
            polling_interval=2.0,
            max_attempts=10
        )