from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base

# SQLite database file
DB_URL = "sqlite:///./autoapply.db"

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Creates the database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
