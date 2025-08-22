#!/usr/bin/env python3
"""
CLI script to create the first admin user for SocialMaestro
"""

import asyncio
import sys
import getpass
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database.database import SessionLocal, engine, Base
from database.models import User
from auth.security import get_password_hash, validate_password_strength, UserRole
from datetime import datetime

def create_admin_user():
    """Interactive CLI to create the first admin user"""

    print("🚀 SocialMaestro - Admin User Setup")
    print("=" * 50)

    # Create database tables if they don't exist
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Check if any users already exist
    db = SessionLocal()
    try:
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"❌ Error: {existing_users} user(s) already exist in the database.")
            print("   Use the web interface to create additional users.")
            return False

        print("✅ Database is empty. Ready to create first admin user.")
        print()

        # Get user input
        while True:
            email = input("Admin email: ").strip()
            if "@" in email and "." in email:
                break
            print("❌ Please enter a valid email address")

        while True:
            full_name = input("Full name: ").strip()
            if len(full_name) >= 2:
                break
            print("❌ Full name must be at least 2 characters")

        while True:
            password = getpass.getpass("Password: ")
            if validate_password_strength(password):
                break
            print("❌ Password must be at least 8 characters with uppercase, lowercase, digit, and special character")

        while True:
            confirm_password = getpass.getpass("Confirm password: ")
            if password == confirm_password:
                break
            print("❌ Passwords do not match")

        # Create admin user
        print("\n🔒 Creating admin user...")

        hashed_password = get_password_hash(password)

        admin_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Name: {admin_user.full_name}")
        print(f"   Role: {admin_user.role}")
        print(f"   User ID: {admin_user.id}")

        print("\n🎉 Setup complete!")
        print("You can now:")
        print("1. Start the API server: uvicorn main:app --reload")
        print("2. Login at: http://localhost:8000/docs")
        print("3. Create additional users via the API")

        return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def check_bootstrap_status():
    """Check if bootstrap is needed"""
    print("Checking bootstrap status...")

    db = SessionLocal()
    try:
        user_count = db.query(User).count()

        if user_count == 0:
            print("✅ Bootstrap needed - no users exist")
            return True
        else:
            print(f"❌ Bootstrap not needed - {user_count} user(s) already exist")
            return False
    finally:
        db.close()

def main():
    """Main CLI function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            check_bootstrap_status()
        elif command == "create":
            if check_bootstrap_status():
                create_admin_user()
            else:
                print("Use the web API to create additional users.")
        else:
            print("Usage:")
            print("  python create_admin.py status  - Check if bootstrap is needed")
            print("  python create_admin.py create  - Create the first admin user")
    else:
        # Interactive mode
        if check_bootstrap_status():
            print()
            response = input("Would you like to create the first admin user? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                create_admin_user()
        else:
            print("Use the web API to create additional users.")

if __name__ == "__main__":
    main()
