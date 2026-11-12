"""
Seed script — create initial data for development.
Creates a default tenant, store, super admin, and default configurations.

Usage:
    python -m scripts.seed_data
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def seed():
    """Seed the database with initial data."""
    from app.core import get_settings
    from app.core.database import async_session_factory, init_db
    from app.core.security import hash_password
    from app.infrastructure.models.auth import User
    from app.infrastructure.models.config import ConfigurationMaster
    from app.infrastructure.models.tenant import Store, Tenant

    settings = get_settings()

    # Initialize database tables
    await init_db()

    async with async_session_factory() as session:
        try:
            # ── 1. Create Default Tenant ──
            tenant = Tenant(
                name="Default Business",
                slug="default-business",
                description="Default tenant for development",
                email="admin@example.com",
                phone="+919876543210",
                website="https://example.com",
                city="Mumbai",
                state="Maharashtra",
                country="India",
                postal_code="400001",
                is_active=True,
            )
            session.add(tenant)
            await session.flush()
            print(f"✅ Tenant created: {tenant.name} (ID: {tenant.id})")

            # ── 2. Create Default Store ──
            store = Store(
                tenant_id=tenant.id,
                name="Main Store",
                slug="main-store",
                description="Primary online store",
                email="store@example.com",
                primary_color="#1E40AF",
                secondary_color="#F59E0B",
                font_family="Inter",
                currency_code="INR",
                timezone="Asia/Kolkata",
                is_active=True,
            )
            session.add(store)
            await session.flush()
            print(f"✅ Store created: {store.name} (ID: {store.id})")

            # ── 3. Create Super Admin ──
            admin = User(
                email="admin@example.com",
                password_hash=hash_password("Admin@123"),
                first_name="Super",
                last_name="Admin",
                role="super_admin",
                tenant_id=tenant.id,
                is_active=True,
                is_verified=True,
            )
            session.add(admin)
            await session.flush()
            print(f"✅ Super Admin created: {admin.email} (ID: {admin.id})")

            # ── 4. Create Default Configurations ──
            default_configs = [
                # General
                ("site_name", "E-Commerce Platform", "string", "general", "Site Name", True),
                ("site_description", "Enterprise E-Commerce Platform", "string", "general", "Site Description", True),
                ("site_logo", "/uploads/logo.png", "file_url", "general", "Site Logo", True),
                ("site_favicon", "/uploads/favicon.ico", "file_url", "general", "Site Favicon", True),
                ("contact_email", "support@example.com", "string", "general", "Contact Email", True),
                ("contact_phone", "+919876543210", "string", "general", "Contact Phone", True),

                # Theme
                ("primary_color", "#1E40AF", "string", "theme", "Primary Color", True),
                ("secondary_color", "#F59E0B", "string", "theme", "Secondary Color", True),
                ("font_family", "Inter", "string", "theme", "Font Family", True),
                ("dark_mode_enabled", "false", "boolean", "theme", "Dark Mode", True),

                # SEO
                ("meta_title", "E-Commerce Platform - Shop Online", "string", "seo", "Meta Title", True),
                ("meta_description", "Best online shopping experience", "string", "seo", "Meta Description", True),
                ("meta_keywords", "ecommerce,shopping,online", "string", "seo", "Meta Keywords", True),

                # Payment
                ("payment_gateway", "razorpay", "string", "payment", "Payment Gateway", False),
                ("cod_enabled", "true", "boolean", "payment", "Cash on Delivery", False),

                # Tax
                ("gst_enabled", "true", "boolean", "tax", "GST Enabled", False),
                ("gst_percentage", "18", "integer", "tax", "GST Percentage", False),

                # Shipping
                ("free_shipping_threshold", "999", "integer", "shipping", "Free Shipping Above (₹)", False),
                ("default_shipping_charge", "49", "integer", "shipping", "Default Shipping (₹)", False),

                # Currency
                ("default_currency", "INR", "string", "currency", "Default Currency", True),
                ("currency_symbol", "₹", "string", "currency", "Currency Symbol", True),

                # Social Media
                ("facebook_url", "https://facebook.com/yourstore", "string", "social_media", "Facebook", True),
                ("instagram_url", "https://instagram.com/yourstore", "string", "social_media", "Instagram", True),
                ("twitter_url", "https://twitter.com/yourstore", "string", "social_media", "Twitter/X", True),
            ]

            for i, (key, value, type_, category, display, is_public) in enumerate(default_configs):
                config = ConfigurationMaster(
                    tenant_id=tenant.id,
                    config_key=key,
                    config_value=value,
                    config_type=type_,
                    category=category,
                    display_name=display,
                    is_public=is_public,
                    is_editable=True,
                    sort_order=i,
                )
                session.add(config)

            await session.commit()
            print(f"✅ {len(default_configs)} default configurations created")

            print("\n" + "=" * 50)
            print("🚀 Database seeding complete!")
            print("=" * 50)
            print(f"\n📧 Admin Email: admin@example.com")
            print(f"🔑 Admin Password: Admin@123")
            print(f"🏢 Tenant ID: {tenant.id}")
            print(f"🏪 Store ID: {store.id}")
            print(f"\n⚠️  Change these credentials in production!\n")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
