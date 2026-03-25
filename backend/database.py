"""
Database connection and session management for FRS Data Management System.
Uses SQLAlchemy for ORM and PostgreSQL as the database.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connection before using
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Maximum overflow connections
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session.
    Use with FastAPI Depends() to inject database session into route handlers.
    
    Example:
        @app.get("/api/datasets")
        def get_datasets(db: Session = Depends(get_db)):
            return db.query(Dataset).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    from models import Dataset, Unit, SheetData, LocalWorkshop, RemoteWorkshop  # Import models to register them
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def drop_db():
    """
    Drop all database tables.
    WARNING: This will delete all data! Use only for development/testing.
    """
    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped")
