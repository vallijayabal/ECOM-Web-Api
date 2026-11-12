"""
Tenant & Store API routes.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_pagination, require_admin, require_super_admin
from app.schemas.common import PaginatedResponse, PaginationParams, SuccessResponse, TokenPayload
from app.schemas.tenant import (
    CreateStoreRequest,
    CreateTenantRequest,
    StoreResponse,
    TenantResponse,
    UpdateStoreRequest,
    UpdateTenantRequest,
)
from app.services.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["Tenants & Stores"])


# ═══════════════════════════════════════════════════
# Tenant Endpoints
# ═══════════════════════════════════════════════════

@router.post("/", response_model=SuccessResponse, status_code=201)
async def create_tenant(
    request: CreateTenantRequest,
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_super_admin),
):
    """Super Admin: create a new tenant/business."""
    service = TenantService(db)
    tenant = await service.create_tenant(request)
    return SuccessResponse(message="Tenant created", data=tenant.model_dump())


@router.get("/", response_model=PaginatedResponse[TenantResponse])
async def list_tenants(
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_super_admin),
    pagination: PaginationParams = Depends(get_pagination),
):
    """Super Admin: list all tenants."""
    service = TenantService(db)
    tenants, total = await service.list_tenants(pagination.offset, pagination.limit, search)
    return PaginatedResponse(data=tenants, pagination=pagination.create_meta(total))


@router.get("/{tenant_id}", response_model=SuccessResponse)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_admin),
):
    """Get tenant details."""
    service = TenantService(db)
    tenant = await service.get_tenant(tenant_id)
    return SuccessResponse(data=tenant.model_dump())


@router.put("/{tenant_id}", response_model=SuccessResponse)
async def update_tenant(
    tenant_id: int,
    request: UpdateTenantRequest,
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_super_admin),
):
    """Super Admin: update tenant details."""
    service = TenantService(db)
    tenant = await service.update_tenant(tenant_id, request)
    return SuccessResponse(message="Tenant updated", data=tenant.model_dump())


# ═══════════════════════════════════════════════════
# Store Endpoints
# ═══════════════════════════════════════════════════

@router.post("/{tenant_id}/stores", response_model=SuccessResponse, status_code=201)
async def create_store(
    tenant_id: int,
    request: CreateStoreRequest,
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_admin),
):
    """Admin: create a store within a tenant."""
    service = TenantService(db)
    store = await service.create_store(tenant_id, request)
    return SuccessResponse(message="Store created", data=store.model_dump())


@router.get("/{tenant_id}/stores", response_model=PaginatedResponse[StoreResponse])
async def list_stores(
    tenant_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_admin),
    pagination: PaginationParams = Depends(get_pagination),
):
    """Admin: list stores for a tenant."""
    service = TenantService(db)
    stores, total = await service.list_stores(tenant_id, pagination.offset, pagination.limit)
    return PaginatedResponse(data=stores, pagination=pagination.create_meta(total))


@router.get("/stores/{store_id}", response_model=SuccessResponse)
async def get_store(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_admin),
):
    """Get store details."""
    service = TenantService(db)
    store = await service.get_store(store_id)
    return SuccessResponse(data=store.model_dump())


@router.put("/stores/{store_id}", response_model=SuccessResponse)
async def update_store(
    store_id: int,
    request: UpdateStoreRequest,
    db: AsyncSession = Depends(get_db),
    _admin: TokenPayload = Depends(require_admin),
):
    """Admin: update store details."""
    service = TenantService(db)
    store = await service.update_store(store_id, request)
    return SuccessResponse(message="Store updated", data=store.model_dump())
