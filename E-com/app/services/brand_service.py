"""
Brand service.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.infrastructure.models.brand import Brand
from app.infrastructure.repositories.brand_repo import BrandRepository
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.utils.slugify import generate_slug


class BrandService:
    def __init__(self, db: AsyncSession):
        self.repo = BrandRepository(db)

    async def create_brand(self, request: BrandCreate, tenant_id: int, store_id: Optional[int] = None) -> BrandResponse:
        slug = generate_slug(request.name)
        existing = await self.repo.get_by_slug(slug, tenant_id)
        if existing:
            raise AlreadyExistsException("Brand", "name", request.name)

        brand = Brand(
            tenant_id=tenant_id,
            store_id=store_id,
            slug=slug,
            **request.model_dump()
        )
        brand = await self.repo.create(brand)
        return BrandResponse.model_validate(brand)

    async def get_brand(self, brand_id: int, tenant_id: int) -> BrandResponse:
        brand = await self.repo.get_by_id(brand_id, tenant_id)
        if not brand:
            raise NotFoundException("Brand", brand_id)
        return BrandResponse.model_validate(brand)

    async def update_brand(self, brand_id: int, request: BrandUpdate, tenant_id: int) -> BrandResponse:
        brand = await self.repo.get_by_id(brand_id, tenant_id)
        if not brand:
            raise NotFoundException("Brand", brand_id)
            
        update_data = request.model_dump(exclude_unset=True)
        if "name" in update_data and update_data["name"] != brand.name:
            slug = generate_slug(update_data["name"])
            existing = await self.repo.get_by_slug(slug, tenant_id)
            if existing and existing.id != brand.id:
                raise AlreadyExistsException("Brand", "name", update_data["name"])
            brand.slug = slug

        for key, value in update_data.items():
            setattr(brand, key, value)

        brand = await self.repo.update(brand)
        return BrandResponse.model_validate(brand)

    async def delete_brand(self, brand_id: int, tenant_id: int) -> None:
        brand = await self.repo.get_by_id(brand_id, tenant_id)
        if not brand:
            raise NotFoundException("Brand", brand_id)
        await self.repo.delete(brand)

    async def list_brands(
        self, tenant_id: int, offset: int = 0, limit: int = 20, search: Optional[str] = None
    ) -> tuple[list[BrandResponse], int]:
        brands, total = await self.repo.list_all(tenant_id, offset, limit, search)
        return [BrandResponse.model_validate(b) for b in brands], total
