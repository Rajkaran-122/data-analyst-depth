-- PostgreSQL initialization script
-- This runs automatically when the database container starts for the first time

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance (optional, Alembic will handle most)
-- These are created here for convenience

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
END $$;
