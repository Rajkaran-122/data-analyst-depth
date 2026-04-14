import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite for local development
if not DATABASE_URL or DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = "sqlite:///./data_analyst.db"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    # Production PostgreSQL (Render/Supabase)
    # Handle "postgres://" vs "postgresql://" fix for SQLAlchemy
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

def init_db():
    """Ensure all tables are created."""
    # We import models here to ensure they are registered with Base metadata
    import models
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency injection to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
