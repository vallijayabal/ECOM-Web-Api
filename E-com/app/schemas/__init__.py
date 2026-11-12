"""
Common Pydantic schemas used across the application.
Includes response wrappers, pagination, token payloads, etc.
"""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


# ═══════════════════════════════════════════════════
# Standard API Response Wrappers
# ═══════════════════════════════════════════════════

class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    message: str
    details: Optional[Any] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with metadata."""
    success: bool = True
    message: str = "Data retrieved successfully"
    data: list[T] = []
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


# ═══════════════════════════════════════════════════
# Pagination Parameters
# ═══════════════════════════════════════════════════

class PaginationParams(BaseModel):
    """Parsed pagination query parameters."""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    def create_meta(self, total_items: int) -> PaginationMeta:
        """Create pagination metadata from total count."""
        total_pages = max(1, -(-total_items // self.page_size))  # Ceiling division
        return PaginationMeta(
            page=self.page,
            page_size=self.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=self.page < total_pages,
            has_previous=self.page > 1,
        )


# ═══════════════════════════════════════════════════
# Token Payload
# ═══════════════════════════════════════════════════

class TokenPayload(BaseModel):
    """Decoded JWT token data."""
    user_id: int
    email: str
    role: str
    tenant_id: int


class TokenResponse(BaseModel):
    """JWT token pair response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ═══════════════════════════════════════════════════
# Common Filters
# ═══════════════════════════════════════════════════

class DateRangeFilter(BaseModel):
    """Date range filter for queries."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SearchFilter(BaseModel):
    """Search and sort filter."""
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = Field("asc", pattern="^(asc|desc)$")


# ═══════════════════════════════════════════════════
# ID-based Schemas
# ═══════════════════════════════════════════════════

class IDResponse(BaseModel):
    """Response containing just an ID (for create operations)."""
    id: int


class BulkIDRequest(BaseModel):
    """Request containing a list of IDs (for bulk operations)."""
    ids: list[int] = Field(..., min_length=1, max_length=100)
