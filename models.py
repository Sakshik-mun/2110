from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    profile = relationship("FinancialProfile", uselist=False, back_populates="user")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    monthly_income = Column(Float, default=0)
    monthly_expenses = Column(Float, default=0)
    monthly_emi = Column(Float, default=0)
    total_debt = Column(Float, default=0)
    credit_limit = Column(Float, default=0)
    credit_used = Column(Float, default=0)
    active_loans = Column(Integer, default=0)
    missed_payments = Column(Integer, default=0)
    savings = Column(Float, default=0)
    cibil_score = Column(Integer, default=300)
    goal = Column(String(255), default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="profile")


class ScoreHistory(Base):
    __tablename__ = "score_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    score = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    kind = Column(String(30))  # analysis | chat
    prompt = Column(Text, default="")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
