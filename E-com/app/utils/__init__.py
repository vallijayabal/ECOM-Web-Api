"""
Pagination utilities for SQLAlchemy async queries.
"""

from typing import Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.schemas.common import PaginatedResponse, PaginationMeta, PaginationParams

T = TypeVar("T")


async def paginate(
    db: AsyncSession,
    query: Select,
    params: PaginationParams,
    response_model: type | None = None,
) -> dict[str, Any]:
    """
    Apply pagination to a SQLAlchemy query and return paginated results.

    Returns dict with 'items' and 'pagination' keys.
    """
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Apply offset/limit
    paginated_query = query.offset(params.offset).limit(params.limit)
    result = await db.execute(paginated_query)
    items = list(result.scalars().all())

    # Convert to response model if provided
    if response_model:
        items = [response_model.model_validate(item) for item in items]

    pagination = params.create_meta(total)

    return {
        "items": items,
        "pagination": pagination,
        "total": total,
    }
