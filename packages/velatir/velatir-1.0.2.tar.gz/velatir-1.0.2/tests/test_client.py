import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx

from velatir.client import Client
from velatir.models import VelatirResponse
from velatir.exceptions import VelatirAPIError, VelatirTimeoutError

@pytest.fixture
def mock_httpx_client():
    """Fixture to mock the httpx client"""
    with patch('httpx.AsyncClient') as mock:
        # Configure the mock client
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"reviewTaskId": "test-review-task-id", "state": "Approved"}
        mock_response.raise_for_status = MagicMock()
        
        # Set up the mock to return the mock response
        mock_instance.request.return_value = mock_response
        
        yield mock_instance

class TestClient:
    
    def test_init(self):
        """Test client initialization"""
        client = Client(api_key="test-key", base_url="https://test.api")
        assert client.api_key == "test-key"
        assert client.base_url == "https://test.api"
    
    async def test_create_review_task(self, mock_httpx_client):
        """Test create_review_task method"""
        client = Client(api_key="test-key")
        
        response = await client.create_review_task(
            function_name="test_function",
            args={"param1": "value1"},
            doc="Test docstring",
            llm_explanation="LLM explanation",
            metadata={"priority": "high"},
            parent_review_task_id="parent-id"
        )
        
        # Verify client was called correctly
        mock_httpx_client.request.assert_called_once()
        args, kwargs = mock_httpx_client.request.call_args
        
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == f"{client.base_url}/review-tasks"
        assert kwargs["json"]["functionName"] == "test_function"
        assert kwargs["json"]["args"] == {"param1": "value1"}
        assert kwargs["json"]["doc"] == "Test docstring"
        assert kwargs["json"]["llmExplanation"] == "LLM explanation"
        assert kwargs["json"]["metadata"] == {"priority": "high"}
        assert kwargs["json"]["parentReviewTaskId"] == "parent-id"
        
        # Verify response was parsed correctly
        assert isinstance(response, VelatirResponse)
        assert response.review_task_id == "test-review-task-id"
        assert response.state == "Approved"
    
    async def test_get_review_task_status(self, mock_httpx_client):
        """Test get_review_task_status method"""
        client = Client(api_key="test-key")
        
        response = await client.get_review_task_status("test-review-task-id")
        
        # Verify client was called correctly
        mock_httpx_client.request.assert_called_once()
        args, kwargs = mock_httpx_client.request.call_args
        
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == f"{client.base_url}/review-tasks/test-review-task-id"
        
        # Verify response was parsed correctly
        assert isinstance(response, VelatirResponse)
        assert response.review_task_id == "test-review-task-id"
        assert response.state == "Approved"
    
    async def test_request_api_error(self, mock_httpx_client):
        """Test API error handling"""
        # Configure mock to raise an HTTP error
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.text = '{"message": "Bad request", "code": "invalid_parameter"}'
        error_response.json.return_value = {"message": "Bad request", "code": "invalid_parameter"}
        
        http_error = httpx.HTTPStatusError(
            "Bad request", 
            request=MagicMock(), 
            response=error_response
        )
        mock_httpx_client.request.side_effect = http_error
        
        client = Client(api_key="test-key")
        
        # Verify exception is raised properly
        with pytest.raises(VelatirAPIError) as excinfo:
            await client.create_review_task(
                function_name="test_function",
                args={"param1": "value1"}
            )
        
        assert excinfo.value.message == "Bad request"
        assert excinfo.value.code == "invalid_parameter"
        assert excinfo.value.http_status == 400
    
    async def test_request_timeout(self, mock_httpx_client):
        """Test timeout error handling"""
        # Configure mock to raise a timeout exception
        mock_httpx_client.request.side_effect = httpx.TimeoutException("Connection timed out")
        
        client = Client(api_key="test-key")
        
        # Verify exception is raised properly
        with pytest.raises(VelatirTimeoutError):
            await client.create_review_task(
                function_name="test_function",
                args={"param1": "value1"}
            )
