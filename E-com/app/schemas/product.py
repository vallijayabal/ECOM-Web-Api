"""
Product schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Variants ──

class ProductVariantCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    option1_name: Optional[str] = None
    option1_value: Optional[str] = None
    option2_name: Optional[str] = None
    option2_value: Optional[str] = None
    option3_name: Optional[str] = None
    option3_value: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    weight: Optional[float] = None
    weight_unit: str = "kg"
    is_active: bool = True


class ProductVariantUpdate(ProductVariantCreate):
    sku: Optional[str] = None


class ProductVariantResponse(ProductVariantCreate):
    id: int
    product_id: int
    image_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Images ──

class ProductImageCreate(BaseModel):
    image_url: str
    alt_text: Optional[str] = None
    sort_order: int = 0
    is_primary: bool = False


class ProductImageResponse(ProductImageCreate):
    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Product ──

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)
    compare_at_price: Optional[float] = None
    is_active: bool = True
    is_featured: bool = False
    requires_shipping: bool = True
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

    variants: list[ProductVariantCreate] = []
    images: list[ProductImageCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    requires_shipping: Optional[bool] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    sku: str
    price: float
    compare_at_price: Optional[float] = None
    is_active: bool
    is_featured: bool
    requires_shipping: bool
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    tenant_id: int
    store_id: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    variants: list[ProductVariantResponse] = []
    images: list[ProductImageResponse] = []

    model_config = {"from_attributes": True}
