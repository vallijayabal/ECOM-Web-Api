"""
Configuration schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConfigCreateRequest(BaseModel):
    """Create/update a configuration entry."""
    config_key: str = Field(..., min_length=1, max_length=255)
    config_value: Optional[str] = None
    config_type: str = Field("string", pattern="^(string|integer|boolean|json|file_url)$")
    category: str = Field("general")
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_public: bool = False
    is_editable: bool = True
    sort_order: int = 0
    store_id: Optional[int] = None  # If store-specific


class ConfigBulkRequest(BaseModel):
    """Bulk configuration update."""
    configs: list[ConfigCreateRequest] = Field(..., min_length=1, max_length=100)


class ConfigResponse(BaseModel):
    """Configuration entry response."""
    id: int
    tenant_id: Optional[int] = None
    store_id: Optional[int] = None
    config_key: str
    config_value: Optional[str] = None
    config_type: str
    category: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_public: bool
    is_editable: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConfigValueResponse(BaseModel):
    """Simplified key-value response for public consumption."""
    config_key: str
    config_value: Optional[str] = None
    config_type: str

    model_config = {"from_attributes": True}
