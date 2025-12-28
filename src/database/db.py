from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from .models import Base, Job, Application

# Use absolute path for DB to avoid file not found issues in complex envs if needed, 
# but relative is fine for this project structure usually.
DATABASE_URL = "sqlite:///./autoapply.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def save_jobs(jobs_list):
    """
    Saves a list of jobs to the DB, ignoring duplicates based on URL.
    Returns: Number of new jobs added.
    """
    session = SessionLocal()
    count = 0
    try:
        for job_data in jobs_list:
            if not job_data.url: continue
            
            # Use merge instead of add to keep the original job_data object detached/usable in UI
            # merge() returns the db-bound instance, but we ignore it and keep using job_data
            session.merge(job_data)
            count += 1
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"DB Error save_jobs: {e}")
    finally:
        session.close()
    return count

def mark_job_applied(job_id, status="applied", notes=None):
    """
    Marks a job as applied by creating an Application record.
    Returns: True if successful or already applied, False on error.
    """
    session = SessionLocal()
    try:
        # Check if already applied
        exists = session.query(Application).filter_by(job_id=job_id).first()
        if not exists:
            app = Application(job_id=job_id, status=status, notes=notes)
            session.add(app)
            session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"DB Error marking applied: {e}")
        return False
    finally:
        session.close()

def get_saved_jobs():
    """
    Returns all jobs, eager loading the 'applications' relationship.
    """
    session = SessionLocal()
    try:
        # Eager load applications to avoid DetachedInstanceError when accessing job.applications later
        return session.query(Job).options(joinedload(Job.applications)).order_by(Job.date_posted.desc()).all()
    finally:
        session.close()

def clean_old_jobs(days=30):
    """
    Deletes jobs posted more than 'days' ago.
    Keeps applied jobs to preserve history.
    """
    session = SessionLocal()
    count = 0
    try:
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # logic: Delete jobs where date_posted < cutoff AND id NOT IN applications
        # Simple approach: Get all old jobs, check if applied, delete if not.
        old_jobs = session.query(Job).filter(Job.date_posted < cutoff).all()
        
        for job in old_jobs:
            # Check if this job has an application
            # We need to check the relationship or query Application table
            is_applied = session.query(Application).filter_by(job_id=job.id).first()
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

def delete_job(job_id):
    """Deletes a single job by ID."""
    session = SessionLocal()
    try:
        job = session.query(Job).filter_by(id=job_id).first()
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
    """Drops all tables and recreates them. DANGEROUS."""
    try:
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
