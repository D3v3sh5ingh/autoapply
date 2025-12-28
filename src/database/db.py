from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from .models import Base, Job, Application, User
from datetime import datetime, timedelta
import os

# Use persistent volume for data (Fly.io mounts at /data)
DATA_DIR = os.getenv("DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)

# Engine cache to avoid creating new engines on every call
_ENGINE_CACHE = {}

def get_user_db_path(user_id: int) -> str:
    """Get database path for specific user."""
    user_dir = os.path.join(DATA_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    return f"sqlite:///{os.path.join(user_dir, 'jobs.db')}"

def get_user_engine(user_id: int):
    """Get or create cached engine for user's database."""
    if user_id not in _ENGINE_CACHE:
        user_db_url = get_user_db_path(user_id)
        _ENGINE_CACHE[user_id] = create_engine(
            user_db_url, 
            connect_args={"check_same_thread": False}
        )
        # Ensure tables exist
        Base.metadata.create_all(bind=_ENGINE_CACHE[user_id])
    return _ENGINE_CACHE[user_id]

def get_user_session(user_id: int):
    """Get a scoped session for user's database."""
    engine = get_user_engine(user_id)
    return scoped_session(sessionmaker(bind=engine))

# Main DB for user accounts only
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'users.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# ===== USER MANAGEMENT =====

def get_or_create_user(provider: str, provider_user_id: str, email: str, name: str) -> int:
    """
    Get existing user by provider+provider_id or create new one.
    Uses provider_user_id as immutable identity (not email).
    Returns: user_id
    """
    session = SessionLocal()
    try:
        # Look up by provider identity (immutable)
        user = session.query(User).filter_by(
            oauth_provider=provider,
            oauth_provider_id=provider_user_id
        ).first()
        
        if user:
            # Update email/name if changed
            if user.email != email or user.name != name:
                user.email = email
                user.name = name
                session.commit()
            return user.id
        
        # Create new user
        new_user = User(
            email=email, 
            name=name, 
            oauth_provider=provider,
            oauth_provider_id=provider_user_id
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user.id
    finally:
        session.close()

def get_user_by_id(user_id: int):
    """Get user details by ID."""
    session = SessionLocal()
    try:
        return session.query(User).filter_by(id=user_id).first()
    finally:
        session.close()

# ===== JOB OPERATIONS (USER-SCOPED) =====

def save_jobs(jobs_list, user_id: int):
    """
    Saves a list of jobs to the user's DB, ignoring duplicates based on URL.
    Returns: Number of new jobs added.
    """
    UserSession = get_user_session(user_id)
    session = UserSession()
    count = 0
    try:
        for job_data in jobs_list:
            if not job_data.url: 
                continue
            
            # Check if job already exists for this user
            existing = session.query(Job).filter_by(url=job_data.url, user_id=user_id).first()
            if existing:
                continue
            
            # Create new Job instance (safer than merge)
            job = Job(
                user_id=user_id,
                title=job_data.title,
                company=job_data.company,
                location=job_data.location,
                description=job_data.description,
                url=job_data.url,
                date_posted=job_data.date_posted,
                source=job_data.source,
                match_score=job_data.match_score,
                keywords_matched=job_data.keywords_matched
            )
            session.add(job)
            count += 1
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"DB Error save_jobs: {e}")
    finally:
        session.close()
    return count

def mark_job_applied(job_id: int, user_id: int, status="applied", notes=None):
    """
    Marks a job as applied by creating an Application record.
    Returns: True if successful or already applied, False on error.
    """
    UserSession = get_user_session(user_id)
    session = UserSession()
    try:
        # Check if already applied
        exists = session.query(Application).filter_by(job_id=job_id, user_id=user_id).first()
        if not exists:
            app = Application(job_id=job_id, user_id=user_id, status=status, notes=notes)
            session.add(app)
            session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"DB Error marking applied: {e}")
        return False
    finally:
        session.close()

def get_saved_jobs(user_id: int):
    """
    Returns all jobs for specific user, eager loading the 'applications' relationship.
    """
    UserSession = get_user_session(user_id)
    session = UserSession()
    try:
        # Eager load applications to avoid DetachedInstanceError when accessing job.applications later
        return session.query(Job).filter_by(user_id=user_id).options(joinedload(Job.applications)).order_by(Job.date_posted.desc()).all()
    finally:
        session.close()

def clean_old_jobs(user_id: int, days=30):
    """
    Deletes jobs posted more than 'days' ago for specific user.
    Keeps applied jobs to preserve history.
    """
    UserSession = get_user_session(user_id)
    session = UserSession()
    count = 0
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get old jobs for this user (now using correct DB)
        old_jobs = session.query(Job).filter(Job.user_id == user_id, Job.date_posted < cutoff).all()
        
        for job in old_jobs:
            # Check if this job has an application
            is_applied = session.query(Application).filter_by(job_id=job.id, user_id=user_id).first()
            if not is_applied:
                session.delete(job)
                count += 1
                
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Cleanup Error: {e}")
    finally:
        session.close()
    return count

def delete_job(job_id: int, user_id: int):
    """Deletes a single job by ID for specific user."""
    UserSession = get_user_session(user_id)
    session = UserSession()
    try:
        job = session.query(Job).filter_by(id=job_id, user_id=user_id).first()
        if job:
            session.delete(job)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Delete Error: {e}")
        return False
    finally:
        session.close()

def reset_db():
    """
    Drops all tables and recreates them. DANGEROUS.
    Only allowed in dev mode.
    """
    if os.getenv("ENV") != "dev":
        raise RuntimeError("reset_db() is disabled in production. Set ENV=dev to enable.")
    
    try:
        # Only reset users.db, not user data folders
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"Reset DB Error: {e}")
        return False

def init_db():
    """Creates the database tables."""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
