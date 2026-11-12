"""
Brand repository.
"""
from typing import Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.brand import Brand


class BrandRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, brand: Brand) -> Brand:
        self.db.add(brand)
        await self.db.flush()
        await self.db.refresh(brand)
        return brand

    async def get_by_id(self, brand_id: int, tenant_id: int) -> Optional[Brand]:
        result = await self.db.execute(
            select(Brand).where(
                and_(Brand.id == brand_id, Brand.tenant_id == tenant_id, Brand.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
        
    async def get_by_slug(self, slug: str, tenant_id: int) -> Optional[Brand]:
        result = await self.db.execute(
            select(Brand).where(
                and_(Brand.slug == slug, Brand.tenant_id == tenant_id, Brand.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, brand: Brand) -> Brand:
        await self.db.flush()
        await self.db.refresh(brand)
        return brand

    async def delete(self, brand: Brand) -> None:
        brand.is_deleted = True
        await self.db.flush()

    async def list_all(
        self, tenant_id: int, offset: int = 0, limit: int = 20, search: Optional[str] = None
    ) -> tuple[list[Brand], int]:
        query = select(Brand).where(
            and_(Brand.tenant_id == tenant_id, Brand.is_deleted == False)
        )
        
        if search:
            query = query.where(Brand.name.ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(Brand.sort_order, Brand.name).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
