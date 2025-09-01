"""
Preprocessing related request and response models.
"""
from typing import List, Dict, Any
from pydantic import BaseModel


class CreatePreprocessorRequest(BaseModel):
    """Request to create a preprocessor."""
    preprocessor_name: str
    preprocessor_description: str
    stages: List[Dict[str, Any]]
    deltas: List[Dict[str, Any]]
    versions: Dict[str, str]


class CreatePreprocessorResponse(BaseModel):
    """Response from preprocessor creation."""
    preprocessor_id: str
    version_id: str


class AddPreprocessorVersionRequest(BaseModel):
    """Request to add a preprocessor version."""
    preprocessor_id: str
    stages: List[Dict[str, Any]]
    deltas: List[Dict[str, Any]]
    versions: Dict[str, str]


class AddPreprocessorVersionResponse(BaseModel):
    """Response from adding a preprocessor version."""
    version_id: str


class UpdatePreprocessorVersionRequest(BaseModel):
    """Request to update a preprocessor version."""
    version_id: str
    stages: List[Dict[str, Any]]
    deltas: List[Dict[str, Any]]
    versions: Dict[str, str]


class UpdatePreprocessorVersionResponse(BaseModel):
    """Response from updating a preprocessor version."""
    version_id: str


class PreprocessorInfo(BaseModel):
    """Information about a preprocessor."""
    preprocessor_id: str
    name: str
    description: str
    created_by: str
    created: str
    team_id: str