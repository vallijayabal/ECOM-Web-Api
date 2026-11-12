"""
Category repository.
"""
from typing import Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.category import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, category: Category) -> Category:
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def get_by_id(self, category_id: int, tenant_id: int) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                and_(Category.id == category_id, Category.tenant_id == tenant_id, Category.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
        
    async def get_by_slug(self, slug: str, tenant_id: int) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(
                and_(Category.slug == slug, Category.tenant_id == tenant_id, Category.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, category: Category) -> Category:
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        category.is_deleted = True
        await self.db.flush()

    async def list_all(
        self, tenant_id: int, parent_id: Optional[int] = None
    ) -> list[Category]:
        query = select(Category).where(
            and_(Category.tenant_id == tenant_id, Category.is_deleted == False)
        )
        if parent_id is not None:
            query = query.where(Category.parent_id == parent_id)
        elif parent_id == 0:
             # special case: fetch only root categories
             query = query.where(Category.parent_id.is_(None))

        query = query.order_by(Category.sort_order, Category.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())
