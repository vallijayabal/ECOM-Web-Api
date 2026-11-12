"""
Application-wide constants.
"""


class UserRoles:
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    CUSTOMER = "customer"

    ALL = [SUPER_ADMIN, ADMIN, MANAGER, STAFF, CUSTOMER]
    ADMIN_ROLES = [SUPER_ADMIN, ADMIN, MANAGER]
    STAFF_ROLES = [SUPER_ADMIN, ADMIN, MANAGER, STAFF]


class OrderStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"

    ALL = [
        PENDING, CONFIRMED, PROCESSING, SHIPPED,
        OUT_FOR_DELIVERY, DELIVERED, CANCELLED, RETURNED, REFUNDED,
    ]


class PaymentStatus:
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

    ALL = [PENDING, AUTHORIZED, CAPTURED, FAILED, REFUNDED, PARTIALLY_REFUNDED]


class ConfigCategories:
    GENERAL = "general"
    THEME = "theme"
    SEO = "seo"
    PAYMENT = "payment"
    SHIPPING = "shipping"
    TAX = "tax"
    EMAIL = "email"
    SMS = "sms"
    NOTIFICATION = "notification"
    SOCIAL_MEDIA = "social_media"
    CURRENCY = "currency"
    LANGUAGE = "language"

    ALL = [
        GENERAL, THEME, SEO, PAYMENT, SHIPPING, TAX,
        EMAIL, SMS, NOTIFICATION, SOCIAL_MEDIA, CURRENCY, LANGUAGE,
    ]


# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Cache TTLs (seconds)
CACHE_TTL_SHORT = 300        # 5 minutes
CACHE_TTL_MEDIUM = 1800      # 30 minutes
CACHE_TTL_LONG = 3600        # 1 hour
CACHE_TTL_VERY_LONG = 86400  # 24 hours
