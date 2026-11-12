"""
Tenant and Store schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ═══════════════════════════════════════════════════
# Tenant Schemas
# ═══════════════════════════════════════════════════

class CreateTenantRequest(BaseModel):
    """Create a new tenant/business."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    description: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    tax_id: Optional[str] = None


class UpdateTenantRequest(BaseModel):
    """Update tenant details."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    tax_id: Optional[str] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    """Tenant data response."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    tax_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════
# Store Schemas
# ═══════════════════════════════════════════════════

class CreateStoreRequest(BaseModel):
    """Create a new store within a tenant."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    secondary_color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    font_family: Optional[str] = None
    currency_code: str = "INR"
    timezone: str = "Asia/Kolkata"


class UpdateStoreRequest(BaseModel):
    """Update store details."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    secondary_color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")
    font_family: Optional[str] = None
    currency_code: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(BaseModel):
    """Store data response."""
    id: int
    tenant_id: int
    name: str
    slug: str
    description: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    font_family: Optional[str] = None
    currency_code: str
    timezone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
