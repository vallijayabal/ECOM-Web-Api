"""
Inventory models for stock tracking.
"""

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel


class Inventory(BaseModel):
    """
    Inventory allocation for a specific product variant in a specific store (or warehouse).
    """

    __tablename__ = "inventory"

    variant_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    store_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("stores.id", ondelete="CASCADE"), nullable=True, index=True,
    )

    # Stock figures
    quantity: Mapped[int] = mapped_column(default=0, server_default="0")
    reserved_quantity: Mapped[int] = mapped_column(default=0, server_default="0")
    
    # Low stock alerts
    low_stock_threshold: Mapped[int] = mapped_column(default=5, server_default="5")

    # Location
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bin_location: Mapped[str | None] = mapped_column(String(100), nullable=True)

    variant: Mapped["ProductVariant"] = relationship("ProductVariant")
    store: Mapped["Store"] = relationship("Store")

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity
