"""
Auth service — business logic for authentication and user management.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AlreadyExistsException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.core.security import (
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.infrastructure.models.auth import AuditLog, RefreshToken, User
from app.infrastructure.repositories.auth_repo import AuthRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    CreateUserRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)
from app.schemas.common import TokenPayload


class AuthService:
    """Business logic for authentication."""

    MAX_FAILED_ATTEMPTS = 5
    LOCK_DURATION_MINUTES = 30

    def __init__(self, db: AsyncSession):
        self.repo = AuthRepository(db)
        self.db = db

    async def register(self, request: RegisterRequest) -> UserResponse:
        """Register a new user."""
        # Check if email already exists in this tenant
        existing = await self.repo.get_user_by_email(request.email, request.tenant_id)
        if existing:
            raise AlreadyExistsException("User", "email", request.email)

        # Create user
        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role="customer",
            tenant_id=request.tenant_id,
            is_active=True,
        )
        user = await self.repo.create_user(user)

        # Audit log
        await self._audit("user_register", user.id, user.tenant_id, "user", user.id)

        return UserResponse.model_validate(user)

    async def login(self, request: LoginRequest, ip_address: Optional[str] = None) -> LoginResponse:
        """Authenticate user and return tokens."""
        user = await self.repo.get_user_by_email(request.email, request.tenant_id)

        if not user:
            raise UnauthorizedException("Invalid email or password")

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise ForbiddenException(
                f"Account is locked. Try again after {user.locked_until.isoformat()}"
            )

        # Verify password
        if not verify_password(request.password, user.password_hash):
            await self.repo.increment_failed_login(user.id)

            # Lock account after too many failures
            if user.failed_login_attempts + 1 >= self.MAX_FAILED_ATTEMPTS:
                lock_until = datetime.now(timezone.utc) + timedelta(minutes=self.LOCK_DURATION_MINUTES)
                await self.repo.lock_user(user.id, lock_until)

            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise ForbiddenException("Account is deactivated")

        # Generate tokens
        tokens = create_token_pair(user.id, user.email, user.role, user.tenant_id)

        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token=tokens["refresh_token"],
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            device_info=request.device_info,
            ip_address=ip_address,
        )
        await self.repo.create_refresh_token(refresh_token)

        # Update last login
        await self.repo.update_last_login(user.id)

        # Audit log
        await self._audit("user_login", user.id, user.tenant_id, "user", user.id, ip_address=ip_address)

        return LoginResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    async def refresh_token(self, refresh_token_str: str) -> dict:
        """Refresh access token using a valid refresh token."""
        stored_token = await self.repo.get_refresh_token(refresh_token_str)
        if not stored_token:
            raise UnauthorizedException("Invalid refresh token")

        if stored_token.expires_at < datetime.now(timezone.utc):
            await self.repo.revoke_refresh_token(refresh_token_str)
            raise UnauthorizedException("Refresh token expired")

        # Get user
        user = await self.repo.get_user_by_id(stored_token.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Revoke old refresh token (token rotation)
        await self.repo.revoke_refresh_token(refresh_token_str)

        # Generate new tokens
        tokens = create_token_pair(user.id, user.email, user.role, user.tenant_id)

        # Store new refresh token
        new_refresh = RefreshToken(
            user_id=user.id,
            token=tokens["refresh_token"],
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            device_info=stored_token.device_info,
            ip_address=stored_token.ip_address,
        )
        await self.repo.create_refresh_token(new_refresh)

        return tokens

    async def logout(self, refresh_token_str: str) -> None:
        """Logout by revoking the refresh token."""
        await self.repo.revoke_refresh_token(refresh_token_str)

    async def logout_all_devices(self, user_id: int) -> None:
        """Revoke all refresh tokens for a user."""
        await self.repo.revoke_all_user_tokens(user_id)

    async def change_password(
        self, user_id: int, request: ChangePasswordRequest,
    ) -> None:
        """Change user password."""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        if not verify_password(request.current_password, user.password_hash):
            raise UnauthorizedException("Current password is incorrect")

        user.password_hash = hash_password(request.new_password)
        await self.db.flush()

        # Revoke all refresh tokens (force re-login)
        await self.repo.revoke_all_user_tokens(user_id)

        # Audit log
        await self._audit("password_change", user.id, user.tenant_id, "user", user.id)

    async def get_user(self, user_id: int) -> UserResponse:
        """Get user profile."""
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return UserResponse.model_validate(user)

    async def create_user(
        self, request: CreateUserRequest, tenant_id: int,
    ) -> UserResponse:
        """Admin creates a new user within the tenant."""
        existing = await self.repo.get_user_by_email(request.email, tenant_id)
        if existing:
            raise AlreadyExistsException("User", "email", request.email)

        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role=request.role,
            tenant_id=tenant_id,
            is_active=True,
        )
        user = await self.repo.create_user(user)
        await self._audit("user_created_by_admin", user.id, tenant_id, "user", user.id)
        return UserResponse.model_validate(user)

    async def list_users(
        self,
        tenant_id: int,
        offset: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[list[UserResponse], int]:
        """List users for a tenant."""
        users, total = await self.repo.list_users(tenant_id, offset, limit, role, search)
        return [UserResponse.model_validate(u) for u in users], total

    # ── Private Helpers ──

    async def _audit(
        self,
        action: str,
        user_id: int,
        tenant_id: int,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Create an audit log entry."""
        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
        )
        await self.repo.create_audit_log(log)
