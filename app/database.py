"""
database.py  –  SQLite schema for leads and conversation state
"""
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./state.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ConversationState(Base):
    """Tracks where each user is in the lead capture flow."""
    __tablename__ = "conversation_state"

    id          = Column(Integer, primary_key=True, index=True)
    phone       = Column(String, unique=True, index=True)
    step        = Column(String, default="none")
    name        = Column(String, nullable=True)
    interest    = Column(String, nullable=True)
    user_phone  = Column(String, nullable=True)  
    email       = Column(String, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
