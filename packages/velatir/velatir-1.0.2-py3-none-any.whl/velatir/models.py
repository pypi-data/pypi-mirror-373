"""
Data models for the Velatir SDK.
"""
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

ReviewTaskState = Literal[
    "Pending",
    "Processing", 
    "Approved",
    "RequiresIntervention",
    "Rejected",
    "ChangeRequested"
]

class VelatirResponse(BaseModel):
    """Response from the Velatir API for a review task request."""
    
    review_task_id: str = Field(alias="reviewTaskId")
    state: ReviewTaskState = Field(alias="state")
    requested_change: Optional[str] = Field(default=None, alias="requestedChange")

    class Config:
        populate_by_name = True
    
    @property
    def is_approved(self) -> bool:
        """Check if the review task is approved."""
        return self.state == "Approved"
    
    @property
    def is_denied(self) -> bool:
        """Check if the review task is denied (final rejection states)."""
        return self.state in ("Rejected", "ChangeRequested")
    
    @property
    def is_pending(self) -> bool:
        """Check if the review task is still pending (waiting states)."""
        return self.state in ("Pending", "Processing", "RequiresIntervention")
    
    @property
    def is_change_requested(self) -> bool:
        """Check if changes are requested for the review task."""
        return self.state == "ChangeRequested"
    
    @property
    def requires_intervention(self) -> bool:
        """Check if the review task requires intervention."""
        return self.state == "RequiresIntervention"
    
    @property
    def is_processing(self) -> bool:
        """Check if the review task is being processed."""
        return self.state == "Processing"