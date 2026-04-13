import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database file in the backend directory
DATABASE_URL = "sqlite:///./data_analyst.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

def get_db():
    """Dependency injection to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
