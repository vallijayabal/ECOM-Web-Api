-- ============================================================
-- E-Commerce Platform — Database Initialization
-- ============================================================

-- Ensure UTF8MB4 encoding
ALTER DATABASE ecom_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges
GRANT ALL PRIVILEGES ON ecom_db.* TO 'ecom_user'@'%';
FLUSH PRIVILEGES;
