-- Create schemas for dbt project
-- This runs automatically when the dbt-db container starts

-- ============================================
-- Users and Roles (matching Snowflake course)
-- ============================================

-- Create preset user for BI dashboards (reporter role)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'preset') THEN
        CREATE USER preset WITH PASSWORD 'preset';
    END IF;
END $$;

-- ============================================
-- Schemas
-- ============================================

-- Raw data schema (source data)
CREATE SCHEMA IF NOT EXISTS raw;

-- Development schema (dbt dev target)
CREATE SCHEMA IF NOT EXISTS dev;

-- Production schema (optional, for dbt prod target)
CREATE SCHEMA IF NOT EXISTS prod;

-- ============================================
-- Permissions for dbt user (TRANSFORM role)
-- Full access to all schemas
-- ============================================
GRANT ALL ON SCHEMA raw TO dbt;
GRANT ALL ON SCHEMA dev TO dbt;
GRANT ALL ON SCHEMA prod TO dbt;

-- ============================================
-- Permissions for preset user (REPORTER role)
-- Read-only access to dev schema (BI dashboards)
-- ============================================
GRANT USAGE ON SCHEMA dev TO preset;
GRANT SELECT ON ALL TABLES IN SCHEMA dev TO preset;
ALTER DEFAULT PRIVILEGES IN SCHEMA dev GRANT SELECT ON TABLES TO preset;

-- ============================================
-- Raw tables matching the course datasets
-- Source: https://dbt-datasets.s3.amazonaws.com/
-- ============================================

-- Listings table
CREATE TABLE IF NOT EXISTS raw.listings (
    id BIGINT PRIMARY KEY,
    listing_url TEXT,
    name TEXT,
    room_type TEXT,
    minimum_nights INTEGER,
    host_id BIGINT,
    price TEXT,  -- Stored as text with $ sign in source
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Hosts table
CREATE TABLE IF NOT EXISTS raw.hosts (
    id BIGINT PRIMARY KEY,
    name TEXT,
    is_superhost TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Reviews table
CREATE TABLE IF NOT EXISTS raw.reviews (
    listing_id BIGINT,
    date DATE,
    reviewer_name TEXT,
    comments TEXT,
    sentiment TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_listings_host_id ON raw.listings(host_id);
CREATE INDEX IF NOT EXISTS idx_reviews_listing_id ON raw.reviews(listing_id);
CREATE INDEX IF NOT EXISTS idx_reviews_date ON raw.reviews(date);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Database initialization complete';
    RAISE NOTICE 'Users: dbt (transform), preset (reporter)';
    RAISE NOTICE 'Schemas: raw, dev, prod';
    RAISE NOTICE 'Tables: raw.listings, raw.hosts, raw.reviews';
END $$;
