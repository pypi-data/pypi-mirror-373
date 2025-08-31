"""Database models for risk detector."""
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Float, JSON, ForeignKey, Integer
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class RiskFeature(Base):
    __tablename__ = "risk_features"
    id = Column(String, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    options = Column(JSON)
    prompt_en = Column(Text, nullable=False)
    help_en = Column(Text)
    required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskRule(Base):
    __tablename__ = "risk_rules"
    id = Column(String, primary_key=True)
    name = Column(Text)
    category = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    condition = Column(JSON, nullable=False)
    legal_refs = Column(JSON, nullable=False)
    related_sections = Column(JSON)
    version = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

class RiskQuestion(Base):
    __tablename__ = "risk_questions"
    id = Column(String, primary_key=True)
    feature_key = Column(String, ForeignKey("risk_features.key"))
    priority = Column(Integer, default=100)
    gating = Column(JSON)
    prompt_en = Column(Text)
    help_en = Column(Text)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(String, primary_key=True)
    customer_id = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rule_snapshot_version = Column(String)
    answers = relationship("ChatAnswer", back_populates="session")
    outcomes = relationship("RiskOutcome", back_populates="session")

class ChatAnswer(Base):
    __tablename__ = "chat_answers"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    feature_key = Column(String)
    value = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSession", back_populates="answers")

class RiskOutcome(Base):
    __tablename__ = "risk_outcomes"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    rule_snapshot_version = Column(String)
    category = Column(String, nullable=False)
    score = Column(Float)
    reasoning = Column(JSON)
    legal_refs = Column(JSON)
    exception_applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    signed_off = Column(Boolean, default=False)
    signed_off_by = Column(String)
    signed_off_at = Column(DateTime)
    session = relationship("ChatSession", back_populates="outcomes")

class MetaKV(Base):
    __tablename__ = "meta_kv"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
