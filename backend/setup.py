#!/usr/bin/env python3
"""
SocialMaestro Backend Setup Script
Installs dependencies and sets up the backend environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True

    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    # Determine pip command based on OS
    pip_cmd = "venv/Scripts/pip" if os.name == "nt" else "venv/bin/pip"

    if not os.path.exists(pip_cmd.split('/')[0]):
        print("❌ Virtual environment not found. Please run setup first.")
        return False

    commands = [
        f"{pip_cmd} install --upgrade pip",
        f"{pip_cmd} install -r requirements.txt"
    ]

    for cmd in commands:
        if not run_command(cmd, f"Installing dependencies with {cmd.split()[-1]}"):
            return False

    return True

def create_env_file():
    """Create .env file from example"""
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True

    if os.path.exists(".env.example"):
        try:
            with open(".env.example", "r") as example:
                content = example.read()

            with open(".env", "w") as env_file:
                env_file.write(content)

            print("✅ Created .env file from .env.example")
            print("⚠️  Please update the .env file with your actual configuration values")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("❌ .env.example not found")
        return False

def main():
    """Main setup function"""
    print("🚀 SocialMaestro Backend Setup")
    print("=" * 40)

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to setup virtual environment")
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        sys.exit(1)

    print("\n" + "=" * 40)
    print("🎉 Backend setup completed successfully!")
    print("\n📝 Next steps:")
    print("   1. Update the .env file with your configuration")
    print("   2. Set up PostgreSQL database:")
    print("      - Install PostgreSQL")
    print("      - Create database: socialmaestro_db")
    print("      - Create user: socialmaestro_user")
    print("   3. Initialize the database:")
    print("      python scripts/init_db.py")
    print("   4. Start the development server:")
    print("      python main.py")
    print("\n💡 For detailed setup instructions, see SETUP.md")

if __name__ == "__main__":
    main()
