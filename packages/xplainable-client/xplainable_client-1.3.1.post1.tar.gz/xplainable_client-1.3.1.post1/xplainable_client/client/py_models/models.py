"""
ML Model related request and response models.
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class CreateModelRequest(BaseModel):
    """Request to create a new model."""
    name: str
    description: str
    type: str
    target_name: str
    algorithm: str
    partition_on: Optional[str] = None
    versions: Dict[str, str]
    partitions: List[Dict[str, Any]]


class CreateModelResponse(BaseModel):
    """Response from model creation."""
    model_id: str
    version_id: str


class AddVersionRequest(BaseModel):
    """Request to add a new version to an existing model."""
    model_id: str
    partition_on: Optional[str] = None
    versions: Dict[str, str]
    partitions: List[Dict[str, Any]]


class AddVersionResponse(BaseModel):
    """Response from adding a model version."""
    version_id: str


class ModelInfo(BaseModel):
    """Information about a model."""
    model_id: str
    # Support both naming conventions from the server
    model_name: Optional[str] = None  # Server returns this
    name: Optional[str] = None  # Expected name
    model_description: Optional[str] = None  # Server returns this
    description: Optional[str] = None  # Expected name
    model_type: Optional[str] = None  # Server returns this
    type: Optional[str] = None  # Expected name
    target_name: Optional[str] = None
    algorithm: Optional[str] = None
    created_by: Optional[str] = None
    user: Optional[Dict] = None  # Server returns user object
    created: Optional[datetime] = None
    deployment_id: Optional[str] = None
    active_version: Optional[str] = None
    deployed: Optional[bool] = None
    active_deployment: Optional[bool] = None
    contributors: Optional[List] = None
    versions: Optional[List] = None
    number_of_versions: Optional[int] = None
    archived: Optional[bool] = None
    active: Optional[bool] = None
    
    @property
    def display_name(self) -> str:
        """Get the name, checking both field names."""
        return self.name or self.model_name or "Unknown"
    
    @property
    def display_description(self) -> str:
        """Get the description, checking both field names."""
        return self.description or self.model_description or ""
    
    @property
    def display_type(self) -> str:
        """Get the type, checking both field names."""
        return self.type or self.model_type or "unknown"


class UserInfo(BaseModel):
    """User information embedded in responses."""
    user_id: str
    username: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    position: Optional[str] = None
    image: Optional[str] = None


class LinkedPreprocessor(BaseModel):
    """Linked preprocessor information."""
    preprocessor_id: str
    version_id: str


class ModelVersion(BaseModel):
    """Information about a model version."""
    version_id: str
    model_id: str
    version_number: int
    created_by: Optional[UserInfo] = None  # Now expects a user object, not string
    created: datetime
    published: Optional[bool] = None
    partitions: Optional[int] = None
    xplainable_version: str
    python_version: str
    linked_preprocessor: Optional[LinkedPreprocessor] = None