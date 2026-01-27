"""
Database Configuration Module

Provides SQLAlchemy engine, session management, and base model.
Implements connection pooling for production use.
"""

from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import QueuePool
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create Base class for declarative models
Base = declarative_base()

# Synchronous engine configuration
SYNC_DATABASE_URL = settings.database_url

engine = create_engine(
    SYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_pre_ping=True,  # Enable connection health checks
    echo=settings.database_echo,
)

# Synchronous session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields a database session and ensures it's closed after use.
    Usage in FastAPI:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined by models inheriting from Base.
    Should be called once at application startup or during migrations.
    """
    # Import all models to ensure they're registered with Base
    from app.models import user, dataset, workspace, report, query, settings_model, activity
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_db_connection() -> bool:
    """
    Check database connectivity.
    
    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


# Connection event listeners for monitoring
@event.listens_for(engine, "connect")
def on_connect(dbapi_conn, connection_record):
    """Log when a new connection is established."""
    logger.debug("Database connection established")


@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from pool."""
    logger.debug("Database connection checked out from pool")


@event.listens_for(engine, "checkin")
def on_checkin(dbapi_conn, connection_record):
    """Log when a connection is returned to pool."""
    logger.debug("Database connection returned to pool")
