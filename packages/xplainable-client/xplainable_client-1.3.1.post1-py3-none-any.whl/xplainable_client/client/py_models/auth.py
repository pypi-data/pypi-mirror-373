"""
Authentication and connection models.
"""
from datetime import datetime
from pydantic import BaseModel


class ClientConnectResponse(BaseModel):
    """Response from client connect endpoint."""
    username: str
    key: str
    expires: datetime