"""
Miscellaneous utilities and model loading related models.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class PingResponse(BaseModel):
    """Response from ping endpoints."""
    success: bool
    response_time: Optional[float] = None
    timestamp: Optional[str] = None


class VersionInfo(BaseModel):
    """Version information."""
    xplainable_version: str
    python_version: str
    client_version: Optional[str] = None


class ModelLoadRequest(BaseModel):
    """Request to load a model."""
    model_id: str
    version_id: str
    include_metadata: bool = True


class LoadedModelInfo(BaseModel):
    """Information about a loaded model."""
    model_id: str
    version_id: str
    model_type: str
    algorithm: str
    target_name: str
    feature_count: int
    partition_count: int
    metadata: Optional[Dict[str, Any]] = None


class ModelPartition(BaseModel):
    """Model partition information."""
    partition_name: str
    feature_importances: Dict[str, float]
    base_value: float
    evaluation_metrics: Optional[Dict[str, Any]] = None
    calibration_data: Optional[Dict[str, Any]] = None


class HealthCheckRequest(BaseModel):
    """Health check request."""
    check_database: bool = True
    check_storage: bool = True
    check_compute: bool = True


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str  # healthy, degraded, unhealthy
    checks: Dict[str, bool]
    details: Optional[Dict[str, Any]] = None
    timestamp: str