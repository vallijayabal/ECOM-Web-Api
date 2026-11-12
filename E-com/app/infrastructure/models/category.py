"""
Category model for hierarchical product categorization.
"""

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import TenantBaseModel


class Category(TenantBaseModel):
    """
    Product category. Supports parent-child relationships (tree structure).
    """

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Hierarchy
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True,
    )

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")

    # SEO Attributes
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    parent: Mapped["Category"] = relationship(
        "Category", remote_side="Category.id", backref="children",
    )
    # Store scoping (if none, available to all stores in tenant)
    store_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
