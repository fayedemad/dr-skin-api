from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./drskin.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Allow SQLite connections across threads
    echo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """
    Dependency for getting database session.
    Usage:
        @router.get("/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 