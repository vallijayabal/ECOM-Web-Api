"""
Config repository — data access for ConfigurationMaster.
"""

from typing import Optional

from sqlalchemy import select, and_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.config import ConfigurationMaster


class ConfigRepository:
    """Data access operations for ConfigurationMaster."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_config(
        self,
        config_key: str,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> Optional[ConfigurationMaster]:
        """Get a single configuration by key with tenant/store scope."""
        conditions = [
            ConfigurationMaster.config_key == config_key,
            ConfigurationMaster.is_deleted == False,
        ]
        if tenant_id is not None:
            conditions.append(ConfigurationMaster.tenant_id == tenant_id)
        else:
            conditions.append(ConfigurationMaster.tenant_id.is_(None))

        if store_id is not None:
            conditions.append(ConfigurationMaster.store_id == store_id)
        else:
            conditions.append(ConfigurationMaster.store_id.is_(None))

        result = await self.db.execute(
            select(ConfigurationMaster).where(and_(*conditions))
        )
        return result.scalar_one_or_none()

    async def get_configs_by_category(
        self,
        category: str,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> list[ConfigurationMaster]:
        """Get all configurations in a category."""
        conditions = [
            ConfigurationMaster.category == category,
            ConfigurationMaster.is_deleted == False,
        ]
        if tenant_id is not None:
            conditions.append(ConfigurationMaster.tenant_id == tenant_id)
        if store_id is not None:
            conditions.append(ConfigurationMaster.store_id == store_id)

        result = await self.db.execute(
            select(ConfigurationMaster)
            .where(and_(*conditions))
            .order_by(ConfigurationMaster.sort_order, ConfigurationMaster.config_key)
        )
        return list(result.scalars().all())

    async def get_all_configs(
        self,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
        public_only: bool = False,
    ) -> list[ConfigurationMaster]:
        """Get all configurations for a tenant/store."""
        conditions = [ConfigurationMaster.is_deleted == False]

        if tenant_id is not None:
            conditions.append(ConfigurationMaster.tenant_id == tenant_id)
        if store_id is not None:
            conditions.append(ConfigurationMaster.store_id == store_id)
        if public_only:
            conditions.append(ConfigurationMaster.is_public == True)

        result = await self.db.execute(
            select(ConfigurationMaster)
            .where(and_(*conditions))
            .order_by(ConfigurationMaster.category, ConfigurationMaster.sort_order)
        )
        return list(result.scalars().all())

    async def upsert_config(self, config: ConfigurationMaster) -> ConfigurationMaster:
        """Create or update a configuration entry."""
        existing = await self.get_config(
            config.config_key, config.tenant_id, config.store_id,
        )
        if existing:
            existing.config_value = config.config_value
            existing.config_type = config.config_type
            existing.category = config.category
            existing.display_name = config.display_name
            existing.description = config.description
            existing.is_public = config.is_public
            existing.is_editable = config.is_editable
            existing.sort_order = config.sort_order
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            self.db.add(config)
            await self.db.flush()
            await self.db.refresh(config)
            return config

    async def delete_config(
        self,
        config_key: str,
        tenant_id: Optional[int] = None,
        store_id: Optional[int] = None,
    ) -> bool:
        """Soft-delete a configuration entry."""
        config = await self.get_config(config_key, tenant_id, store_id)
        if config:
            config.is_deleted = True
            await self.db.flush()
            return True
        return False

    async def bulk_upsert(self, configs: list[ConfigurationMaster]) -> list[ConfigurationMaster]:
        """Bulk upsert configurations."""
        results = []
        for config in configs:
            result = await self.upsert_config(config)
            results.append(result)
        return results
