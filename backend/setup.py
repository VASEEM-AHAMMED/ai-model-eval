#!/usr/bin/env python3
"""
Setup script for AI Model Evaluation Platform.
Helps with environment setup and deployment preparation.
"""

import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path

def create_directories():
    """Create necessary directories for the application"""
    directories = ['uploads', 'exports', 'samples']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create a template .env file if it doesn't exist"""
    env_path = Path('.env')
    
    if env_path.exists():
        print("⚠️ .env file already exists. Skipping.")
        return False
    
    with open(env_path, 'w') as f:
        f.write("""# Database Configuration
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_model_eval

# Security
SECRET_KEY=your_secret_key_here_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional Settings
FORCE_POSTGRES=false  # Set to true to prevent SQLite fallback
""")
    
    print("✅ Created template .env file.")
    print("⚠️ Make sure to update the .env file with your actual configuration.")
    return True

def check_dependencies():
    """Check if required system dependencies are installed"""
    requirements = {
        "PostgreSQL": ["psql", "--version"],
        "Python 3.8+": ["python3", "--version"],
    }
    
    all_good = True
    
    print("Checking system dependencies:")
    for name, command in requirements.items():
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {name}: {version}")
            else:
                print(f"❌ {name}: Not found or error running command")
                all_good = False
        except FileNotFoundError:
            print(f"❌ {name}: Not found")
            all_good = False
    
    return all_good

def setup_virtualenv():
    """Set up a virtual environment and install dependencies"""
    venv_dir = "venv"
    
    if os.path.exists(venv_dir):
        print(f"⚠️ Virtual environment already exists at {venv_dir}. Skipping creation.")
    else:
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
            print(f"✅ Created virtual environment at {venv_dir}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    # Determine the pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
    else:
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
    
    print("Installing dependencies...")
    try:
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Installed dependencies")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup script for AI Model Evaluation Platform")
    parser.add_argument("--check-deps", action="store_true", help="Check system dependencies")
    parser.add_argument("--create-dirs", action="store_true", help="Create necessary directories")
    parser.add_argument("--create-env", action="store_true", help="Create template .env file")
    parser.add_argument("--setup-venv", action="store_true", help="Set up virtual environment and install dependencies")
    parser.add_argument("--all", action="store_true", help="Perform all setup tasks")
    
    args = parser.parse_args()
    
    # If no arguments provided, run all tasks
    if not any(vars(args).values()):
        args.all = True
    
    if args.all or args.check_deps:
        check_dependencies()
    
    if args.all or args.create_dirs:
        create_directories()
    
    if args.all or args.create_env:
        create_env_file()
    
    if args.all or args.setup_venv:
        setup_virtualenv()
    
    print("\n✅ Setup complete!")
    print("Next steps:")
    print("1. Update the .env file with your database configuration")
    print("2. Create the database: createdb ai_model_eval")
    print("3. Run the application: python -m uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    main() 