from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Job(Base):
    __tablename__ = 'jobs'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(500), unique=True)
    date_posted: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default='unknown')  # e.g., 'linkedin', 'indeed'
    
    # Matching data
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    keywords_matched: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    applications: Mapped[List["Application"]] = relationship(back_populates="job")

class Application(Base):
    __tablename__ = 'applications'

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey('jobs.id'))
    status: Mapped[str] = mapped_column(String(50), default='applied')  # applied, interview, offer, rejected
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_applied: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    job: Mapped["Job"] = relationship(back_populates="applications")

class Profile(Base):
    __tablename__ = 'profiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # locations, job types, etc.
