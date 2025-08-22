#!/usr/bin/env python3
"""
Database initialization script for SocialMaestro
This script sets up the database and creates the initial admin user
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from database.database import init_database, check_database_connection, SessionLocal
from database.models import User
from auth.security import get_password_hash
from config.settings import settings

def create_admin_user(email: str, password: str, full_name: str = "Admin User"):
    """Create the initial admin user"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"⚠️  Admin user with email {email} already exists")
            return existing_user

        # Create new admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role="admin",
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"✅ Admin user created successfully:")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Role: admin")
        print(f"   ID: {admin_user.id}")

        return admin_user

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
        return None
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("🚀 Initializing SocialMaestro Database...")
    print("=" * 50)

    # Check database connection
    print("1. Checking database connection...")
    if not check_database_connection():
        print("❌ Database connection failed. Please check your DATABASE_URL in .env file")
        print(f"Current DATABASE_URL: {settings.database_url}")
        sys.exit(1)

    # Initialize database (create tables)
    print("\n2. Creating database tables...")
    if not init_database():
        print("❌ Failed to initialize database")
        sys.exit(1)

    # Create admin user
    print("\n3. Creating admin user...")

    # Check if we should create default admin
    admin_email = os.getenv("ADMIN_EMAIL", "admin@socialmaestro.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "AdminPass123!")
    admin_name = os.getenv("ADMIN_NAME", "SocialMaestro Admin")

    admin_user = create_admin_user(
        email=admin_email,
        password=admin_password,
        full_name=admin_name
    )

    if not admin_user:
        print("❌ Failed to create admin user")
        sys.exit(1)

    # Summary
    print("\n" + "=" * 50)
    print("🎉 Database initialization completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Start the backend server: python main.py")
    print("   2. Open http://localhost:8000/docs to view API documentation")
    print("   3. Use the admin credentials to login:")
    print(f"      Email: {admin_email}")
    print(f"      Password: {admin_password}")
    print("\n⚠️  Remember to change the admin password after first login!")

if __name__ == "__main__":
    main()
