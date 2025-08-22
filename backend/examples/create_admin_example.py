#!/usr/bin/env python3
"""
SocialMaestro - Create Admin User Example (Python)
This script demonstrates how to create the first admin user via API using Python
"""

import requests
import json
import sys
from typing import Dict, Optional

API_BASE = "http://localhost:8000/api"

def check_bootstrap_status() -> Dict:
    """Check if bootstrap is needed"""
    try:
        response = requests.get(f"{API_BASE}/auth/bootstrap/status")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking bootstrap status: {e}")
        sys.exit(1)

def create_admin_user(email: str, full_name: str, password: str) -> Dict:
    """Create admin user via bootstrap endpoint"""
    admin_data = {
        "email": email,
        "full_name": full_name,
        "password": password,
        "confirm_password": password
    }

    try:
        response = requests.post(
            f"{API_BASE}/auth/bootstrap",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating admin user: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)

def login_user(email: str, password: str) -> str:
    """Login and get access token"""
    login_data = {
        "email": email,
        "password": password
    }

    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error logging in: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)

def get_user_info(access_token: str) -> Dict:
    """Get current user information"""
    try:
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting user info: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        sys.exit(1)

def main():
    """Main function"""
    print("🚀 SocialMaestro - Admin Setup (Python)")
    print("=" * 50)

    # Check bootstrap status
    print("📋 Checking bootstrap status...")
    status = check_bootstrap_status()
    print(f"Status: {json.dumps(status, indent=2)}")

    if status.get("bootstrap_needed", False):
        print("✅ Bootstrap needed - creating admin user...")

        # Default admin credentials (change these!)
        admin_email = "admin@example.com"
        admin_name = "Admin User"
        admin_password = "AdminPass123!"

        print(f"🔑 Creating admin user: {admin_email}")

        # Create admin user
        admin_user = create_admin_user(admin_email, admin_name, admin_password)
        print("✅ Admin user created:")
        print(json.dumps(admin_user, indent=2, default=str))

        # Login to get token
        print("\n🔐 Logging in as admin...")
        access_token = login_user(admin_email, admin_password)
        print(f"✅ Login successful! Token: {access_token[:50]}...")

        # Test authenticated endpoint
        print("\n🔍 Testing authenticated endpoint...")
        user_info = get_user_info(access_token)
        print("User info:")
        print(json.dumps(user_info, indent=2, default=str))

        # Save token to file
        try:
            with open(".admin_token", "w") as f:
                f.write(access_token)
            print("\n💡 Admin token saved to .admin_token file")
        except Exception as e:
            print(f"⚠️ Could not save token to file: {e}")

        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Change the default admin password")
        print("2. Configure social media API keys in .env")
        print("3. Create additional users via API")
        print("4. Access API docs at: http://localhost:8000/docs")

        # Example of creating another user
        print(f"\n📝 Example: Create another user")
        print("```python")
        print("import requests")
        print("")
        print("# Use the admin token to create another user")
        print(f'token = "{access_token[:20]}..."')
        print("user_data = {")
        print('    "email": "manager@example.com",')
        print('    "full_name": "Marketing Manager",')
        print('    "password": "ManagerPass123!",')
        print('    "role": "manager"')
        print("}")
        print("")
        print(f'response = requests.post("{API_BASE}/auth/register",')
        print('    json=user_data,')
        print('    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}')
        print(")")
        print("```")

    else:
        print("❌ Bootstrap not needed - users already exist")
        print(f"User count: {status.get('user_count', 0)}")
        print("\nUse regular login instead:")
        print("```python")
        print("import requests")
        print("")
        print("login_data = {")
        print('    "email": "your-email@example.com",')
        print('    "password": "your-password"')
        print("}")
        print("")
        print(f'response = requests.post("{API_BASE}/auth/login", json=login_data)')
        print("token = response.json()['access_token']")
        print("```")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
