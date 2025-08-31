-- AI-Mem Database Initialization Script
-- This script sets up initial database configuration for PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if it doesn't exist (for development)
-- Note: This runs after the database is already created by Docker
-- but ensures we have proper permissions and extensions

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE aimem TO aimem_user;
GRANT ALL PRIVILEGES ON DATABASE aimem_dev TO dev_user;

-- Set timezone
SET timezone = 'UTC';