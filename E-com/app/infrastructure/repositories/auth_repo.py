"""
Auth repository — data access for User, RefreshToken, and AuditLog.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.auth import AuditLog, RefreshToken, User


class AuthRepository:
    """Data access operations for authentication entities."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── User Operations ──

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by primary key."""
        result = await self.db.execute(
            select(User).where(and_(User.id == user_id, User.is_deleted == False))
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str, tenant_id: int) -> Optional[User]:
        """Get user by email within a tenant."""
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.email == email,
                    User.tenant_id == tenant_id,
                    User.is_deleted == False,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_last_login(self, user_id: int) -> None:
        """Update the last login timestamp."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                last_login_at=datetime.now(timezone.utc),
                failed_login_attempts=0,
                locked_until=None,
            )
        )

    async def increment_failed_login(self, user_id: int) -> None:
        """Increment failed login counter."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(failed_login_attempts=User.failed_login_attempts + 1)
        )

    async def lock_user(self, user_id: int, until: datetime) -> None:
        """Lock a user account until a specific time."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(locked_until=until)
        )

    async def list_users(
        self,
        tenant_id: int,
        offset: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[list[User], int]:
        """List users with pagination, filtering, and search."""
        query = select(User).where(
            and_(User.tenant_id == tenant_id, User.is_deleted == False)
        )

        if role:
            query = query.where(User.role == role)
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (User.first_name.ilike(search_filter))
                | (User.last_name.ilike(search_filter))
                | (User.email.ilike(search_filter))
            )

        # Count total
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        # Fetch page
        query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        users = list(result.scalars().all())

        return users, total

    # ── Refresh Token Operations ──

    async def create_refresh_token(self, token: RefreshToken) -> RefreshToken:
        """Store a refresh token."""
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_refresh_token(self, token_string: str) -> Optional[RefreshToken]:
        """Get a refresh token by its value."""
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token == token_string,
                    RefreshToken.is_revoked == False,
                )
            )
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_string: str) -> None:
        """Revoke a specific refresh token."""
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token_string)
            .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
        )

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """Revoke all refresh tokens for a user (e.g., password change)."""
        await self.db.execute(
            update(RefreshToken)
            .where(and_(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False))
            .values(is_revoked=True, revoked_at=datetime.now(timezone.utc))
        )

    # ── Audit Log Operations ──

    async def create_audit_log(self, log: AuditLog) -> AuditLog:
        """Create an audit log entry."""
        self.db.add(log)
        await self.db.flush()
        return log

    async def list_audit_logs(
        self,
        tenant_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs with filtering and pagination."""
        query = select(AuditLog).where(AuditLog.is_deleted == False)

        if tenant_id:
            query = query.where(AuditLog.tenant_id == tenant_id)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)

        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total
