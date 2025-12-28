"""
Rate limiter for JobPulse Agent.
Implements soft quotas to protect shared compute resources.
"""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session
from src.database.models import Base

import os
DATA_DIR = os.getenv("DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'users.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class UserUsage(Base):
    __tablename__ = 'user_usage'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    event_type = Column(String(50))  # 'search', 'apply', etc.
    timestamp = Column(DateTime, default=datetime.utcnow)

class RateLimiter:
    """Manages usage quotas and rate limits per user."""
    
    DAILY_SEARCH_LIMIT = 40
    SEARCH_COOLDOWN_SECONDS = 15
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        
    def can_search(self) -> tuple[bool, str]:
        """
        Check if user can perform a search.
        Returns: (allowed: bool, message: str)
        """
        session = SessionLocal()
        try:
            # Check daily limit
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            count = session.query(UserUsage).filter(
                UserUsage.user_id == self.user_id,
                UserUsage.event_type == 'search',
                UserUsage.timestamp >= today_start
            ).count()
            
            if count >= self.DAILY_SEARCH_LIMIT:
                return False, f"⏱️ Daily search limit reached ({self.DAILY_SEARCH_LIMIT} searches/day). Try again tomorrow!"
            
            # Check cooldown
            last_search = session.query(UserUsage).filter(
                UserUsage.user_id == self.user_id,
                UserUsage.event_type == 'search'
            ).order_by(UserUsage.timestamp.desc()).first()
            
            if last_search:
                time_since = (datetime.utcnow() - last_search.timestamp).total_seconds()
                if time_since < self.SEARCH_COOLDOWN_SECONDS:
                    wait_time = int(self.SEARCH_COOLDOWN_SECONDS - time_since)
                    return False, f"⏳ Please wait {wait_time}s before your next search (prevents overload)"
            
            return True, ""
            
        finally:
            session.close()
    
    def record_search(self):
        """Record a search event."""
        session = SessionLocal()
        try:
            usage = UserUsage(user_id=self.user_id, event_type='search')
            session.add(usage)
            session.commit()
        finally:
            session.close()
    
    def get_usage_today(self) -> dict:
        """Get user's usage stats for today."""
        session = SessionLocal()
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            searches = session.query(UserUsage).filter(
                UserUsage.user_id == self.user_id,
                UserUsage.event_type == 'search',
                UserUsage.timestamp >= today_start
            ).count()
            
            return {
                'searches': searches,
                'searches_remaining': max(0, self.DAILY_SEARCH_LIMIT - searches)
            }
        finally:
            session.close()

def init_rate_limiter_table():
    """Create the usage tracking table if it doesn't exist."""
    Base.metadata.create_all(bind=engine, tables=[UserUsage.__table__])
