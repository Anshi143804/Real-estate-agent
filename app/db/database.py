"""
Database configuration.

Responsibilities:
- Load PostgreSQL connection
- Create SQLAlchemy engine
- Create database sessions
- Provide Base class for ORM models
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables
load_dotenv()
from urllib.parse import quote_plus
import os

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD", ""))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}"
)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment.")

# SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    echo=True,          # Prints SQL queries during development
    pool_pre_ping=True  # Prevents stale DB connections
)

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all ORM models
class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency.

    Usage:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()