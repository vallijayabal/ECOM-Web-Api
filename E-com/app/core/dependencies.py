"""
FastAPI dependency injection functions.
Provides current user, tenant context, role-based access, pagination, etc.
"""

from typing import Optional

import jwt
from fastapi import Depends, Header, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_settings
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.redis import CacheService, get_redis
from app.core.security import decode_token
from app.schemas.common import PaginationParams, TokenPayload

settings = get_settings()
security = HTTPBearer(auto_error=False)


# ═══════════════════════════════════════════════════
# Authentication Dependencies
# ═══════════════════════════════════════════════════

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> TokenPayload:
    """
    Extract and validate JWT token from Authorization header.
    Returns the decoded token payload.
    """
    if credentials is None:
        raise UnauthorizedException("Authentication required")

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")

        return TokenPayload(
            user_id=int(payload["sub"]),
            email=payload["email"],
            role=payload["role"],
            tenant_id=payload["tenant_id"],
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired")
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise UnauthorizedException("Invalid token")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[TokenPayload]:
    """Same as get_current_user but returns None if no token provided."""
    if credentials is None:
        return None
    try:
        return await get_current_user(credentials)
    except UnauthorizedException:
        return None


# ═══════════════════════════════════════════════════
# Role-Based Access Control
# ═══════════════════════════════════════════════════

class RoleChecker:
    """
    Dependency that checks if the current user has one of the allowed roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(RoleChecker(["admin", "super_admin"]))])
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if user.role not in self.allowed_roles:
            raise ForbiddenException(
                f"Role '{user.role}' does not have access. Required: {self.allowed_roles}"
            )
        return user


# Convenience role checkers
require_super_admin = RoleChecker(["super_admin"])
require_admin = RoleChecker(["super_admin", "admin"])
require_manager = RoleChecker(["super_admin", "admin", "manager"])
require_staff = RoleChecker(["super_admin", "admin", "manager", "staff"])


# ═══════════════════════════════════════════════════
# Pagination Dependency
# ═══════════════════════════════════════════════════

async def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
) -> PaginationParams:
    """Parse pagination parameters from query string."""
    return PaginationParams(page=page, page_size=page_size)


# ═══════════════════════════════════════════════════
# Cache Dependency
# ═══════════════════════════════════════════════════

async def get_cache() -> CacheService:
    """Get a CacheService instance."""
    redis = await get_redis()
    return CacheService(redis)
