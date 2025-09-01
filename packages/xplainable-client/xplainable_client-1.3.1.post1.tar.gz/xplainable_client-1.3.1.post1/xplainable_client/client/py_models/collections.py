"""
Collections related request and response models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreateCollectionRequest(BaseModel):
    """Request to create a collection."""
    model_id: str
    name: str
    description: str


class CreateCollectionResponse(BaseModel):
    """Response from collection creation."""
    collection_id: str


class UpdateCollectionNameRequest(BaseModel):
    """Request to update collection name."""
    name: str


class UpdateCollectionDescriptionRequest(BaseModel):
    """Request to update collection description."""
    description: str


class CreateScenariosRequest(BaseModel):
    """Request to create scenarios."""
    scenarios: list[dict]


class CollectionInfo(BaseModel):
    """Information about a collection."""
    collection_id: Optional[str] = None
    id: Optional[str] = None  # API might return 'id' instead
    model_id: str
    name: str
    description: str
    created_by: str
    created: datetime
    
    @property
    def display_id(self) -> str:
        """Get collection ID from either field."""
        return self.collection_id or self.id or "unknown"


class ScenarioInfo(BaseModel):
    """Information about a scenario."""
    scenario_id: Optional[str] = None
    id: Optional[str] = None  # API might return 'id' instead
    collection_id: str
    name: str
    description: str
    data: dict
    created_by: str
    created: datetime
    
    @property
    def display_id(self) -> str:
        """Get scenario ID from either field."""
        return self.scenario_id or self.id or "unknown"