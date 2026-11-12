"""
Product repository.
"""
from typing import Optional
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models.product import Product, ProductVariant, ProductImage


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def get_by_id(self, product_id: int, tenant_id: int) -> Optional[Product]:
        """Get product with its variants and images eager-loaded."""
        result = await self.db.execute(
            select(Product)
            .options(
                selectinload(Product.variants),
                selectinload(Product.images)
            )
            .where(
                and_(Product.id == product_id, Product.tenant_id == tenant_id, Product.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()
        
    async def get_by_slug(self, slug: str, tenant_id: int) -> Optional[Product]:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.variants), selectinload(Product.images))
            .where(
                and_(Product.slug == slug, Product.tenant_id == tenant_id, Product.is_deleted == False)
            )
        )
        return result.scalar_one_or_none()

    async def update(self, product: Product) -> Product:
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        product.is_deleted = True
        await self.db.flush()

    async def list_all(
        self, 
        tenant_id: int, 
        offset: int = 0, 
        limit: int = 20, 
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> tuple[list[Product], int]:
        query = select(Product).options(
            selectinload(Product.variants),
            selectinload(Product.images)
        ).where(
            and_(Product.tenant_id == tenant_id, Product.is_deleted == False)
        )
        
        if category_id:
            query = query.where(Product.category_id == category_id)
        if brand_id:
            query = query.where(Product.brand_id == brand_id)
        if search:
            query = query.where(
                (Product.name.ilike(f"%{search}%")) | (Product.sku.ilike(f"%{search}%"))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(Product.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total
