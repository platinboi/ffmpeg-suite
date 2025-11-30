"""
PostgreSQL Database Service for Templates
Uses Neon PostgreSQL for production-grade template storage
"""

import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import logging
from typing import Optional, Dict, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseService:
    """Handles PostgreSQL database connections and operations with connection pooling"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://neondb_owner:npg_Y3uQc9xVXgze@ep-bitter-frog-ahv64lf5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
        )
        self._connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool"""
        try:
            self._connection_pool = pool.SimpleConnectionPool(
                minconn=2,      # Minimum 2 connections always open
                maxconn=10,     # Maximum 10 concurrent connections
                dsn=self.database_url
            )
            logger.info("✓ Database connection pool initialized (2-10 connections)")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections from pool"""
        conn = None
        try:
            # Get connection from pool
            conn = self._connection_pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                # Return connection to pool instead of closing
                self._connection_pool.putconn(conn)

    def close_pool(self):
        """Close all connections in the pool (call on shutdown)"""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("✓ Database connection pool closed")

    def init_templates_table(self):
        """Create templates table if it doesn't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    font_path VARCHAR(500) NOT NULL,
                    font_size INTEGER NOT NULL,
                    font_weight INTEGER DEFAULT 500,
                    text_color VARCHAR(50) NOT NULL,
                    border_width INTEGER NOT NULL,
                    border_color VARCHAR(50) NOT NULL,
                    shadow_x INTEGER NOT NULL,
                    shadow_y INTEGER NOT NULL,
                    shadow_color VARCHAR(50) NOT NULL,
                    position VARCHAR(50) NOT NULL,
                    background_enabled BOOLEAN NOT NULL,
                    background_color VARCHAR(50) NOT NULL,
                    background_opacity FLOAT NOT NULL,
                    text_opacity FLOAT NOT NULL,
                    alignment VARCHAR(20) DEFAULT 'center',
                    max_text_width_percent INTEGER DEFAULT 80,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_default BOOLEAN DEFAULT FALSE
                )
            """)

            # Create indexes for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_templates_name
                ON templates(name)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_templates_created_at
                ON templates(created_at)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_templates_is_default
                ON templates(is_default)
            """)

            # Migration: Add max_text_width_percent column if it doesn't exist
            # This handles existing tables that were created before this column was added
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'templates'
                        AND column_name = 'max_text_width_percent'
                    ) THEN
                        ALTER TABLE templates
                        ADD COLUMN max_text_width_percent INTEGER DEFAULT 80;
                    END IF;
                END $$;
            """)

            # Migration: Add line_spacing column if it doesn't exist
            # This handles existing tables that were created before this column was added
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'templates'
                        AND column_name = 'line_spacing'
                    ) THEN
                        ALTER TABLE templates
                        ADD COLUMN line_spacing INTEGER DEFAULT -8;
                    END IF;
                END $$;
            """)

            # Create updated_at trigger
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            """)

            cursor.execute("""
                DROP TRIGGER IF EXISTS update_templates_updated_at ON templates
            """)

            cursor.execute("""
                CREATE TRIGGER update_templates_updated_at
                BEFORE UPDATE ON templates
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
            """)

            logger.info("✓ Templates table initialized")

    def check_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
