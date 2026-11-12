"""
Product models: Product, ProductVariant, ProductImage.
"""

from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel, TenantBaseModel


class Product(TenantBaseModel):
    """
    Core product entity.
    """

    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    short_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    long_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Identifiers
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Pricing (Base Price)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    compare_at_price: Mapped[float | None] = mapped_column(Float(asdecimal=True), nullable=True)

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    requires_shipping: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    # Grouping
    category_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    brand_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True,
    )

    # Scope
    store_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    # SEO Attributes
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    category: Mapped["Category"] = relationship("Category")
    brand: Mapped["Brand"] = relationship("Brand")


class ProductVariant(BaseModel):
    """
    Variations of a product (e.g., Size, Color).
    """

    __tablename__ = "product_variants"

    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # E.g., option1_name = "Color", option1_value = "Red"
    option1_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    option1_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    option2_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    option2_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    option3_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    option3_value: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Pricing overrides
    price: Mapped[float | None] = mapped_column(Float(asdecimal=True), nullable=True)
    compare_at_price: Mapped[float | None] = mapped_column(Float(asdecimal=True), nullable=True)

    # Weight
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight_unit: Mapped[str] = mapped_column(String(20), default="kg", server_default="kg")

    image_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("product_images.id", ondelete="SET NULL"), nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    product: Mapped["Product"] = relationship("Product", back_populates="variants")


class ProductImage(BaseModel):
    """
    Images associated with a product.
    """

    __tablename__ = "product_images"

    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, server_default="0")
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    product: Mapped["Product"] = relationship("Product", back_populates="images")
