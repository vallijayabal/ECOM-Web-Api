"""
Category service.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.infrastructure.models.category import Category
from app.infrastructure.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse
from app.utils.slugify import generate_slug


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.repo = CategoryRepository(db)

    async def create_category(self, request: CategoryCreate, tenant_id: int, store_id: int | None = None) -> CategoryResponse:
        slug = generate_slug(request.name)
        existing = await self.repo.get_by_slug(slug, tenant_id)
        if existing:
            raise AlreadyExistsException("Category", "name", request.name)
        
        # Verify parent exists if provided
        if request.parent_id:
            parent = await self.repo.get_by_id(request.parent_id, tenant_id)
            if not parent:
                raise NotFoundException("Parent Category", request.parent_id)

        category = Category(
            tenant_id=tenant_id,
            store_id=store_id,
            slug=slug,
            **request.model_dump()
        )
        category = await self.repo.create(category)
        return CategoryResponse.model_validate(category)

    async def get_category(self, category_id: int, tenant_id: int) -> CategoryResponse:
        category = await self.repo.get_by_id(category_id, tenant_id)
        if not category:
            raise NotFoundException("Category", category_id)
        return CategoryResponse.model_validate(category)

    async def update_category(self, category_id: int, request: CategoryUpdate, tenant_id: int) -> CategoryResponse:
        category = await self.repo.get_by_id(category_id, tenant_id)
        if not category:
            raise NotFoundException("Category", category_id)
            
        update_data = request.model_dump(exclude_unset=True)
        if "name" in update_data and update_data["name"] != category.name:
            slug = generate_slug(update_data["name"])
            existing = await self.repo.get_by_slug(slug, tenant_id)
            if existing and existing.id != category.id:
                raise AlreadyExistsException("Category", "name", update_data["name"])
            category.slug = slug

        # Prevent circular reference
        if "parent_id" in update_data and update_data["parent_id"] == category.id:
            raise ValueError("Category cannot be its own parent")

        for key, value in update_data.items():
            setattr(category, key, value)

        category = await self.repo.update(category)
        return CategoryResponse.model_validate(category)

    async def delete_category(self, category_id: int, tenant_id: int) -> None:
        category = await self.repo.get_by_id(category_id, tenant_id)
        if not category:
            raise NotFoundException("Category", category_id)
        await self.repo.delete(category)

    async def get_category_tree(self, tenant_id: int) -> list[CategoryTreeResponse]:
        """Builds a nested tree of categories for frontend menus."""
        all_categories = await self.repo.list_all(tenant_id)
        
        # Build dictionary for quick lookup by ID
        cat_dict = {cat.id: CategoryTreeResponse.model_validate(cat) for cat in all_categories}
        
        tree = []
        for cat in all_categories:
            if cat.parent_id is None:
                tree.append(cat_dict[cat.id])
            else:
                parent = cat_dict.get(cat.parent_id)
                if parent:
                    # Initialize children list if missing (for Pydantic validation)
                    parent.children.append(cat_dict[cat.id])
                    
        return tree
