from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

from app.core.config import settings

DATABASE_URL = settings.database_url

Base = declarative_base()

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    github_issue = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    plans = relationship("Plan", back_populates="issue")

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    plan_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    issue = relationship("Issue", back_populates="plans")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    level = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AIResponse(Base):
    __tablename__ = "ai_responses"
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class WorkflowState(Base):
    __tablename__ = "workflow_states"
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, index=True)
    state_data = Column(JSON)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class UserHistory(Base):
    __tablename__ = "user_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    action = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
DBSessionLocal = SessionLocal

def init_db():
    Base.metadata.create_all(bind=engine)
