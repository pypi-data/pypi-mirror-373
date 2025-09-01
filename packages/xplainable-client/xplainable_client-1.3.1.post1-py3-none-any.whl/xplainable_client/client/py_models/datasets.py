"""
Dataset related request and response models.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class DatasetInfo(BaseModel):
    """Information about a dataset."""
    name: str
    description: Optional[str] = None
    size: Optional[int] = None
    rows: Optional[int] = None
    columns: Optional[int] = None
    created: Optional[str] = None
    url: Optional[str] = None


class DatasetListResponse(BaseModel):
    """Response containing list of datasets."""
    datasets: List[DatasetInfo]


class DatasetUploadRequest(BaseModel):
    """Request to upload a dataset."""
    name: str
    description: Optional[str] = None
    team_id: Optional[str] = None


class DatasetUploadResponse(BaseModel):
    """Response from dataset upload."""
    dataset_id: str
    name: str
    status: str