from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Base directory of this file
BASE_DIR = Path(__file__).parent

# Database file path
DB_PATH = BASE_DIR / "patients.db"

# Ensure the directory exists (not strictly needed here since it's the same folder as this file)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLAlchemy database URL using absolute path
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite + FastAPI multithreading
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
