"""
GPT/LLM related request and response models.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class GPTReportRequest(BaseModel):
    """Request for generating GPT reports."""
    model_version_id: str
    target_description: str = "text"
    project_objective: str = "text"
    max_features: int = Field(default=15, ge=1, le=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class GPTReportResponse(BaseModel):
    """Response from GPT report generation."""
    heading: str
    tagline: str
    body: str
    
    @property
    def report(self) -> str:
        """Get the full report content (body)."""
        return self.body
    
    @property
    def key_insights(self) -> Optional[List[str]]:
        """Extract key insights from the body if available."""
        return None  # Could be enhanced to extract insights from body
    
    @property
    def summary(self) -> Optional[str]:
        """Use the tagline as summary."""
        return self.tagline


class ModelExplanationRequest(BaseModel):
    """Request for model explanation in natural language."""
    model_version_id: str
    language: str = "en"
    detail_level: str = Field(default="medium", pattern="^(low|medium|high)$")


class ModelExplanationResponse(BaseModel):
    """Response containing natural language model explanation."""
    explanation: str
    technical_details: Optional[str] = None
    business_context: Optional[str] = None