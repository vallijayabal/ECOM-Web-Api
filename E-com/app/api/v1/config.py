"""
Configuration API routes — dynamic settings management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.schemas.common import SuccessResponse, TokenPayload
from app.schemas.config import (
    ConfigBulkRequest,
    ConfigCreateRequest,
    ConfigResponse,
    ConfigValueResponse,
)
from app.services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["Configuration"])


# ═══════════════════════════════════════════════════
# Public Endpoints
# ═══════════════════════════════════════════════════

@router.get("/public", response_model=SuccessResponse)
async def get_public_configs(
    tenant_id: Optional[int] = Query(None),
    store_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get public configurations (for frontend/clients)."""
    service = ConfigService(db)
    configs = await service.get_public_configs(tenant_id, store_id)
    return SuccessResponse(data=[c.model_dump() for c in configs])


# ═══════════════════════════════════════════════════
# Admin Endpoints
# ═══════════════════════════════════════════════════

@router.get("/", response_model=SuccessResponse)
async def get_all_configs(
    store_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin),
):
    """Admin: get all configurations for the tenant."""
    service = ConfigService(db)
    configs = await service.get_all_configs(admin.tenant_id, store_id)
    return SuccessResponse(data=[c.model_dump() for c in configs])


@router.get("/category/{category}", response_model=SuccessResponse)
async def get_configs_by_category(
    category: str,
    store_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin),
):
    """Admin: get configurations by category."""
    service = ConfigService(db)
    configs = await service.get_configs_by_category(category, admin.tenant_id, store_id)
    return SuccessResponse(data=[c.model_dump() for c in configs])


@router.post("/", response_model=SuccessResponse, status_code=201)
async def set_config(
    request: ConfigCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin),
):
    """Admin: create or update a configuration entry."""
    service = ConfigService(db)
    config = await service.set_config(request, admin.tenant_id)
    return SuccessResponse(message="Configuration saved", data=config.model_dump())


@router.post("/bulk", response_model=SuccessResponse, status_code=201)
async def bulk_set_configs(
    request: ConfigBulkRequest,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin),
):
    """Admin: bulk create/update configurations."""
    service = ConfigService(db)
    configs = await service.bulk_set_configs(request, admin.tenant_id)
    return SuccessResponse(
        message=f"{len(configs)} configurations saved",
        data=[c.model_dump() for c in configs],
    )


@router.delete("/{config_key}", response_model=SuccessResponse)
async def delete_config(
    config_key: str,
    store_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin),
):
    """Admin: delete a configuration entry."""
    service = ConfigService(db)
    await service.delete_config(config_key, admin.tenant_id, store_id)
    return SuccessResponse(message="Configuration deleted")
