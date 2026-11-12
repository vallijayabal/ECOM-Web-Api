"""
Config service — business logic for dynamic configuration management.
"""

import json
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.models.config import ConfigurationMaster
from app.infrastructure.repositories.config_repo import ConfigRepository
from app.schemas.config import (
    ConfigBulkRequest,
    ConfigCreateRequest,
    ConfigResponse,
    ConfigValueResponse,
)


class ConfigService:
    """Business logic for dynamic configuration."""

    def __init__(self, db: AsyncSession):
        self.repo = ConfigRepository(db)

    async def get_config_value(
        self,
        key: str,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get a configuration value with fallback logic:
        1. Store-specific → 2. Tenant-specific → 3. Global → 4. Default
        """
        # Try store-specific first
        if store_id is not None:
            config = await self.repo.get_config(key, tenant_id, store_id)
            if config:
                return config.config_value

        # Try tenant-specific
        if tenant_id is not None:
            config = await self.repo.get_config(key, tenant_id, None)
            if config:
                return config.config_value

        # Try global
        config = await self.repo.get_config(key, None, None)
        if config:
            return config.config_value

        return default

    async def get_typed_value(
        self,
        key: str,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
        default: Any = None,
    ) -> Any:
        """Get a configuration value cast to its declared type."""
        config = None

        if store_id is not None:
            config = await self.repo.get_config(key, tenant_id, store_id)
        if config is None and tenant_id is not None:
            config = await self.repo.get_config(key, tenant_id, None)
        if config is None:
            config = await self.repo.get_config(key, None, None)

        if config is None:
            return default

        return self._cast_value(config.config_value, config.config_type)

    async def set_config(
        self, request: ConfigCreateRequest, tenant_id: Optional[int] = None,
    ) -> ConfigResponse:
        """Create or update a configuration entry."""
        config = ConfigurationMaster(
            config_key=request.config_key,
            config_value=request.config_value,
            config_type=request.config_type,
            category=request.category,
            display_name=request.display_name,
            description=request.description,
            is_public=request.is_public,
            is_editable=request.is_editable,
            sort_order=request.sort_order,
            tenant_id=tenant_id,
            store_id=request.store_id,
        )
        config = await self.repo.upsert_config(config)
        return ConfigResponse.model_validate(config)

    async def bulk_set_configs(
        self, request: ConfigBulkRequest, tenant_id: Optional[int] = None,
    ) -> list[ConfigResponse]:
        """Bulk create/update configurations."""
        results = []
        for config_req in request.configs:
            result = await self.set_config(config_req, tenant_id)
            results.append(result)
        return results

    async def get_configs_by_category(
        self,
        category: str,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> list[ConfigResponse]:
        """Get all configs in a category."""
        configs = await self.repo.get_configs_by_category(category, tenant_id, store_id)
        return [ConfigResponse.model_validate(c) for c in configs]

    async def get_all_configs(
        self,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> list[ConfigResponse]:
        """Get all configurations for a tenant/store."""
        configs = await self.repo.get_all_configs(tenant_id, store_id)
        return [ConfigResponse.model_validate(c) for c in configs]

    async def get_public_configs(
        self,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> list[ConfigValueResponse]:
        """Get public configurations (for frontend consumption)."""
        configs = await self.repo.get_all_configs(tenant_id, store_id, public_only=True)
        return [ConfigValueResponse.model_validate(c) for c in configs]

    async def delete_config(
        self,
        key: str,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> None:
        """Delete a configuration entry."""
        deleted = await self.repo.delete_config(key, tenant_id, store_id)
        if not deleted:
            raise NotFoundException("Configuration", key)

    @staticmethod
    def _cast_value(value: Optional[str], config_type: str) -> Any:
        """Cast a string value to its declared type."""
        if value is None:
            return None

        try:
            if config_type == "integer":
                return int(value)
            elif config_type == "boolean":
                return value.lower() in ("true", "1", "yes")
            elif config_type == "json":
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            return value
