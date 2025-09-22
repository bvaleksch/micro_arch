from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

DATABASE_URL = "sqlite:///./db.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


