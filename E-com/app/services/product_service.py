"""
Product service.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.infrastructure.models.product import Product, ProductVariant, ProductImage
from app.infrastructure.repositories.product_repo import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.slugify import generate_slug


class ProductService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)

    async def create_product(self, request: ProductCreate, tenant_id: int, store_id: Optional[int] = None) -> ProductResponse:
        slug = generate_slug(request.name)
        existing = await self.repo.get_by_slug(slug, tenant_id)
        if existing:
            raise AlreadyExistsException("Product", "name", request.name)

        product_data = request.model_dump(exclude={"variants", "images"})
        
        product = Product(
            tenant_id=tenant_id,
            store_id=store_id,
            slug=slug,
            **product_data
        )
        
        # Add variants
        for variant_req in request.variants:
            v_data = variant_req.model_dump()
            product.variants.append(ProductVariant(**v_data))
            
        # Add images
        for image_req in request.images:
            i_data = image_req.model_dump()
            product.images.append(ProductImage(**i_data))

        product = await self.repo.create(product)
        return ProductResponse.model_validate(product)

    async def get_product(self, product_id: int, tenant_id: int) -> ProductResponse:
        product = await self.repo.get_by_id(product_id, tenant_id)
        if not product:
            raise NotFoundException("Product", product_id)
        return ProductResponse.model_validate(product)

    async def get_product_by_slug(self, slug: str, tenant_id: int) -> ProductResponse:
        product = await self.repo.get_by_slug(slug, tenant_id)
        if not product:
            raise NotFoundException("Product", slug)
        return ProductResponse.model_validate(product)

    async def update_product(self, product_id: int, request: ProductUpdate, tenant_id: int) -> ProductResponse:
        product = await self.repo.get_by_id(product_id, tenant_id)
        if not product:
            raise NotFoundException("Product", product_id)
            
        update_data = request.model_dump(exclude_unset=True)
        if "name" in update_data and update_data["name"] != product.name:
            slug = generate_slug(update_data["name"])
            existing = await self.repo.get_by_slug(slug, tenant_id)
            if existing and existing.id != product.id:
                raise AlreadyExistsException("Product", "name", update_data["name"])
            product.slug = slug

        for key, value in update_data.items():
            setattr(product, key, value)

        product = await self.repo.update(product)
        return ProductResponse.model_validate(product)

    async def delete_product(self, product_id: int, tenant_id: int) -> None:
        product = await self.repo.get_by_id(product_id, tenant_id)
        if not product:
            raise NotFoundException("Product", product_id)
        await self.repo.delete(product)

    async def list_products(
        self, 
        tenant_id: int, 
        offset: int = 0, 
        limit: int = 20,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> tuple[list[ProductResponse], int]:
        products, total = await self.repo.list_all(tenant_id, offset, limit, category_id, brand_id, search)
        return [ProductResponse.model_validate(p) for p in products], total
