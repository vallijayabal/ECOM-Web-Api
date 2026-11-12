"""
Tenant service — business logic for tenant and store management.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.infrastructure.models.tenant import Store, Tenant
from app.infrastructure.repositories.tenant_repo import TenantRepository
from app.schemas.tenant import (
    CreateStoreRequest,
    CreateTenantRequest,
    StoreResponse,
    TenantResponse,
    UpdateStoreRequest,
    UpdateTenantRequest,
)


class TenantService:
    """Business logic for tenant and store management."""

    def __init__(self, db: AsyncSession):
        self.repo = TenantRepository(db)

    # ── Tenant Operations ──

    async def create_tenant(self, request: CreateTenantRequest) -> TenantResponse:
        """Create a new tenant/business."""
        existing = await self.repo.get_tenant_by_slug(request.slug)
        if existing:
            raise AlreadyExistsException("Tenant", "slug", request.slug)

        tenant = Tenant(**request.model_dump())
        tenant = await self.repo.create_tenant(tenant)
        return TenantResponse.model_validate(tenant)

    async def get_tenant(self, tenant_id: int) -> TenantResponse:
        """Get tenant by ID."""
        tenant = await self.repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise NotFoundException("Tenant", tenant_id)
        return TenantResponse.model_validate(tenant)

    async def update_tenant(
        self, tenant_id: int, request: UpdateTenantRequest,
    ) -> TenantResponse:
        """Update tenant details."""
        tenant = await self.repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise NotFoundException("Tenant", tenant_id)

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tenant, key, value)

        tenant = await self.repo.update_tenant(tenant)
        return TenantResponse.model_validate(tenant)

    async def list_tenants(
        self, offset: int = 0, limit: int = 20, search: Optional[str] = None,
    ) -> tuple[list[TenantResponse], int]:
        """List all tenants."""
        tenants, total = await self.repo.list_tenants(offset, limit, search)
        return [TenantResponse.model_validate(t) for t in tenants], total

    # ── Store Operations ──

    async def create_store(
        self, tenant_id: int, request: CreateStoreRequest,
    ) -> StoreResponse:
        """Create a store within a tenant."""
        # Verify tenant exists
        tenant = await self.repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise NotFoundException("Tenant", tenant_id)

        # Check slug uniqueness
        existing = await self.repo.get_store_by_slug(request.slug)
        if existing:
            raise AlreadyExistsException("Store", "slug", request.slug)

        store = Store(tenant_id=tenant_id, **request.model_dump())
        store = await self.repo.create_store(store)
        return StoreResponse.model_validate(store)

    async def get_store(self, store_id: int) -> StoreResponse:
        """Get store by ID."""
        store = await self.repo.get_store_by_id(store_id)
        if not store:
            raise NotFoundException("Store", store_id)
        return StoreResponse.model_validate(store)

    async def update_store(
        self, store_id: int, request: UpdateStoreRequest,
    ) -> StoreResponse:
        """Update store details."""
        store = await self.repo.get_store_by_id(store_id)
        if not store:
            raise NotFoundException("Store", store_id)

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(store, key, value)

        store = await self.repo.update_store(store)
        return StoreResponse.model_validate(store)

    async def list_stores(
        self, tenant_id: int, offset: int = 0, limit: int = 20,
    ) -> tuple[list[StoreResponse], int]:
        """List stores for a tenant."""
        stores, total = await self.repo.list_stores_by_tenant(tenant_id, offset, limit)
        return [StoreResponse.model_validate(s) for s in stores], total
