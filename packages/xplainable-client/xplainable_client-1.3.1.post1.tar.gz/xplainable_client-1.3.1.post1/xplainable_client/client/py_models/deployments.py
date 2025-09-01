"""
Deployment related request and response models.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CreateDeploymentRequest(BaseModel):
    """Request to create a deployment."""
    model_version_id: str


class CreateDeploymentResponse(BaseModel):
    """Response from deployment creation."""
    deployment_id: str


class CreateDeploymentKeyRequest(BaseModel):
    """Request to create a deployment key."""
    deployment_id: str
    description: str = ""
    days_until_expiry: int = 90


class CreateDeploymentKeyResponse(BaseModel):
    """Response from deployment key creation."""
    deploy_key: UUID


class DeploymentInfo(BaseModel):
    """Information about a deployment."""
    deployment_id: str
    model_id: str
    version_id: str  # Fixed typo from version_iud
    created_by: str
    created: datetime
    active: bool
    ip_blocking: Optional[bool] = None
    deploy_key_count: Optional[int] = None  # Add field that might be in response


class DeployKeyInfo(BaseModel):
    """Information about a deploy key."""
    key_id: str
    deployment_id: Optional[str] = None
    description: Optional[str] = None
    created: Optional[datetime] = None
    expires: Optional[datetime] = None
    created_by: Optional[str] = None
    active: Optional[bool] = None
    revoked: Optional[bool] = None  # Add field that appears in actual API response