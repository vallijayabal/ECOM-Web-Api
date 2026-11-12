"""
Tenant repository — data access for Tenant and Store.
"""

from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.tenant import Store, Tenant


class TenantRepository:
    """Data access operations for Tenant and Store entities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Tenant Operations ──

    async def create_tenant(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        await self.db.flush()
        await self.db.refresh(tenant)
        return tenant

    async def get_tenant_by_id(self, tenant_id: int) -> Optional[Tenant]:
        result = await self.db.execute(
            select(Tenant).where(and_(Tenant.id == tenant_id, Tenant.is_deleted == False))
        )
        return result.scalar_one_or_none()

    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        result = await self.db.execute(
            select(Tenant).where(and_(Tenant.slug == slug, Tenant.is_deleted == False))
        )
        return result.scalar_one_or_none()

    async def list_tenants(
        self, offset: int = 0, limit: int = 20, search: Optional[str] = None,
    ) -> tuple[list[Tenant], int]:
        query = select(Tenant).where(Tenant.is_deleted == False)
        if search:
            query = query.where(
                Tenant.name.ilike(f"%{search}%") | Tenant.email.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(Tenant.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        tenants = list(result.scalars().all())

        return tenants, total

    async def update_tenant(self, tenant: Tenant) -> Tenant:
        await self.db.flush()
        await self.db.refresh(tenant)
        return tenant

    # ── Store Operations ──

    async def create_store(self, store: Store) -> Store:
        self.db.add(store)
        await self.db.flush()
        await self.db.refresh(store)
        return store

    async def get_store_by_id(self, store_id: int) -> Optional[Store]:
        result = await self.db.execute(
            select(Store).where(and_(Store.id == store_id, Store.is_deleted == False))
        )
        return result.scalar_one_or_none()

    async def get_store_by_slug(self, slug: str) -> Optional[Store]:
        result = await self.db.execute(
            select(Store).where(and_(Store.slug == slug, Store.is_deleted == False))
        )
        return result.scalar_one_or_none()

    async def list_stores_by_tenant(
        self, tenant_id: int, offset: int = 0, limit: int = 20,
    ) -> tuple[list[Store], int]:
        query = select(Store).where(
            and_(Store.tenant_id == tenant_id, Store.is_deleted == False)
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(Store.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        stores = list(result.scalars().all())

        return stores, total

    async def update_store(self, store: Store) -> Store:
        await self.db.flush()
        await self.db.refresh(store)
        return store
