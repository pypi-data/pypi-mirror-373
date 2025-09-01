"""
Inference related request and response models.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request for making predictions."""
    model_id: str
    version_id: str
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    delimiter: str = ","


class PredictionResponse(BaseModel):
    """Response from prediction request."""
    predictions: List[Dict[str, Any]]
    model_id: str
    version_id: str
    threshold: Optional[float] = None
    execution_time: Optional[float] = None


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions."""
    model_id: str
    version_id: str
    data: List[Dict[str, Any]]
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


class BatchPredictionResponse(BaseModel):
    """Response from batch prediction request."""
    predictions: List[Any]
    model_id: str
    version_id: str
    batch_size: int
    execution_time: Optional[float] = None


class ExplanationRequest(BaseModel):
    """Request for model explanations."""
    model_id: str
    version_id: str
    instance: Dict[str, Any]
    num_features: int = 10


class ExplanationResponse(BaseModel):
    """Response containing model explanations."""
    feature_importance: Dict[str, float]
    base_value: float
    prediction: Any
    explanation_text: Optional[str] = None