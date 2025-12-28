"""
Database migration script for multi-user upgrade.
Adds User table and user_id foreign keys to existing tables.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine, text
from src.database.models import Base, User, Job, Application, Profile
from datetime import datetime

DATABASE_URL = "sqlite:///./autoapply.db"

def migrate_to_multiuser():
    """
    Migrate existing single-user database to multi-user schema.
    Creates default admin user and assigns all existing data to them.
    """
    engine = create_engine(DATABASE_URL)
    
    print("🔄 Starting database migration...")
    
    # Check if migration already done
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
        if result.fetchone():
            print("✅ Migration already completed. Users table exists.")
            return
    
    print("📋 Creating new schema...")
    # Create all tables (new ones will be created, existing ones skipped)
    Base.metadata.create_all(bind=engine)
    
    print("👤 Creating default admin user...")
    # Create default admin user
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO users (email, name, oauth_provider, created_at)
            VALUES ('admin@jobpulse.local', 'Admin User', 'local', :now)
        """), {"now": datetime.utcnow()})
        
        # Get the admin user ID
        result = conn.execute(text("SELECT id FROM users WHERE email='admin@jobpulse.local'"))
        admin_id = result.fetchone()[0]
        
        print(f"✅ Created admin user with ID: {admin_id}")
        
        # Check if user_id column exists in jobs table
        result = conn.execute(text("PRAGMA table_info(jobs)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'user_id' not in columns:
            print("🔧 Adding user_id column to existing tables...")
            
            # SQLite doesn't support ADD COLUMN with foreign keys directly
            # We need to recreate tables or add column then create foreign key
            
            # Simpler approach: add column without FK, then populate
            conn.execute(text("ALTER TABLE jobs ADD COLUMN user_id INTEGER"))
            conn.execute(text("ALTER TABLE applications ADD COLUMN user_id INTEGER"))
            conn.execute(text("ALTER TABLE profiles ADD COLUMN user_id INTEGER"))
            
            print("📦 Assigning existing data to admin user...")
            # Assign all existing data to admin user
            conn.execute(text("UPDATE jobs SET user_id = :admin_id"), {"admin_id": admin_id})
            conn.execute(text("UPDATE applications SET user_id = :admin_id"), {"admin_id": admin_id})
            conn.execute(text("UPDATE profiles SET user_id = :admin_id"), {"admin_id": admin_id})
            
            print("✅ Migration complete!")
        else:
            print("✅ Columns already migrated")
    
    print("\n🎉 Database successfully upgraded to multi-user schema!")
    print(f"   Default admin user: admin@jobpulse.local (ID: {admin_id})")
    print("   All existing data has been preserved and assigned to admin user.")

if __name__ == "__main__":
    migrate_to_multiuser()
