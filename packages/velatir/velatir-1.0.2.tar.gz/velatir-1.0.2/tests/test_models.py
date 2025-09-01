"""
Tests for the VelatirResponse model.
"""
import pytest
from velatir.models import VelatirResponse


class TestVelatirResponse:
    """Test VelatirResponse model"""
    
    def test_approved_state(self):
        """Test approved state detection"""
        response = VelatirResponse(
            review_task_id="test-id",
            state="Approved"
        )
        
        assert response.is_approved is True
        assert response.is_denied is False
        assert response.is_pending is False
        assert response.is_processing is False
        assert response.requires_intervention is False
        assert response.is_change_requested is False
    
    def test_rejected_state(self):
        """Test rejected state detection"""
        response = VelatirResponse(
            review_task_id="test-id",
            state="Rejected",
            requested_change="Please fix the errors"
        )
        
        assert response.is_approved is False
        assert response.is_denied is True
        assert response.is_pending is False
        assert response.requested_change == "Please fix the errors"
    
    def test_change_requested_state(self):
        """Test change requested state detection"""
        response = VelatirResponse(
            review_task_id="test-id",
            state="ChangeRequested",
            requested_change="Update parameters"
        )
        
        assert response.is_approved is False
        assert response.is_denied is True
        assert response.is_pending is False
        assert response.is_change_requested is True
        assert response.requested_change == "Update parameters"
    
    def test_pending_state(self):
        """Test pending state detection"""
        response = VelatirResponse(
            review_task_id="test-id",
            state="Pending"
        )
        
        assert response.is_approved is False
        assert response.is_denied is False
        assert response.is_pending is True
        assert response.is_processing is False
        assert response.requires_intervention is False
        assert response.is_change_requested is False
    
    def test_processing_state(self):
        """Test processing state detection"""
        response = VelatirResponse(
            review_task_id="test-id",
            state="Processing"
        )
        
        assert response.is_approved is False
        assert response.is_denied is False
        assert response.is_pending is True
        assert response.is_processing is True
        assert response.requires_intervention is False
        assert response.is_change_requested is False
    
    def test_requires_intervention_state(self):
        """Test requires intervention state detection"""
        response = VelatirResponse(
            review_task_id="test-id",
            state="RequiresIntervention"
        )
        
        assert response.is_approved is False
        assert response.is_denied is False
        assert response.is_pending is True
        assert response.is_processing is False
        assert response.requires_intervention is True
        assert response.is_change_requested is False
    
    def test_field_aliases(self):
        """Test that field aliases work correctly"""
        # Test with API response format (camelCase)
        response = VelatirResponse(
            reviewTaskId="test-id",
            state="Approved",
            requestedChange="Some change"
        )
        
        assert response.review_task_id == "test-id"
        assert response.state == "Approved"
        assert response.requested_change == "Some change"