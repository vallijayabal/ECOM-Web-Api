"""
Product Review models.
"""

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import BaseModel


class Review(BaseModel):
    """
    Product reviews by customers.
    """

    __tablename__ = "reviews"

    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Verification and state
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    product: Mapped["Product"] = relationship("Product")
    user: Mapped["User"] = relationship("User")
