"""
Auth API routes — registration, login, token refresh, user management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRoles
from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_pagination,
    require_admin,
)
from app.schemas.auth import (
    ChangePasswordRequest,
    CreateUserRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    UserResponse,
)
from app.schemas.common import PaginatedResponse, PaginationParams, SuccessResponse, TokenPayload, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=SuccessResponse, status_code=201)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new customer account."""
    service = AuthService(db)
    user = await service.register(request)
    return SuccessResponse(message="Registration successful", data=user.model_dump())


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and get JWT tokens."""
    ip_address = req.client.host if req.client else None
    service = AuthService(db)
    return await service.login(request, ip_address)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using a valid refresh token."""
    service = AuthService(db)
    tokens = await service.refresh_token(request.refresh_token)
    return TokenResponse(**tokens)


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    _user: TokenPayload = Depends(get_current_user),
):
    """Logout by revoking the refresh token."""
    service = AuthService(db)
    await service.logout(request.refresh_token)
    return SuccessResponse(message="Logged out successfully")


@router.post("/logout-all", response_model=SuccessResponse)
async def logout_all_devices(
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    """Logout from all devices."""
    service = AuthService(db)
    await service.logout_all_devices(user.user_id)
    return SuccessResponse(message="Logged out from all devices")


@router.get("/me", response_model=SuccessResponse)
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    """Get current user's profile."""
    service = AuthService(db)
    profile = await service.get_user(user.user_id)
    return SuccessResponse(data=profile.model_dump())


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    user: TokenPayload = Depends(get_current_user),
):
    """Change current user's password."""
    service = AuthService(db)
    await service.change_password(user.user_id, request)
    return SuccessResponse(message="Password changed successfully. Please login again.")


# ═══════════════════════════════════════════════════
# Admin User Management
# ═══════════════════════════════════════════════════

@router.post("/users", response_model=SuccessResponse, status_code=201)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin),
):
    """Admin: create a new user in the tenant."""
    service = AuthService(db)
    user = await service.create_user(request, admin.tenant_id)
    return SuccessResponse(message="User created", data=user.model_dump())


@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: TokenPayload = Depends(require_admin),
    pagination: PaginationParams = Depends(get_pagination),
):
    """Admin: list all users in the tenant."""
    service = AuthService(db)
    users, total = await service.list_users(
        admin.tenant_id, pagination.offset, pagination.limit, role, search,
    )
    return PaginatedResponse(
        data=users,
        pagination=pagination.create_meta(total),
    )
