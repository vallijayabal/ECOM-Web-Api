"""
ConfigurationMaster model — stores all dynamic application settings.
Supports tenant-specific and store-specific configurations.
"""

from sqlalchemy import BigInteger, Boolean, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import BaseModel


class ConfigurationMaster(BaseModel):
    """
    Dynamic configuration table.
    Allows administrators to manage application settings from the database
    without modifying source code.

    Categories: general, theme, seo, payment, shipping, tax,
                email, sms, notification, social_media, currency, language
    """

    __tablename__ = "configuration_master"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "store_id", "config_key",
            name="uq_config_tenant_store_key",
        ),
    )

    # Scope (nullable for global configs)
    tenant_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    store_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    # Config key-value
    config_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    config_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_type: Mapped[str] = mapped_column(
        String(50), default="string", server_default="string",
    )  # string, integer, boolean, json, file_url

    # Metadata
    category: Mapped[str] = mapped_column(
        String(50), default="general", server_default="general", index=True,
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0",
    )  # Whether visible to public APIs
    is_editable: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="1",
    )  # Whether admin can edit

    # Ordering
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")
