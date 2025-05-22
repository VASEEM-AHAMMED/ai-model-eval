import os
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
# Use the current user as default if DB_USER is not set
current_user = os.environ.get("USER", "vaseem")  # Default to 'vaseem' if USER env var not set
DB_USER = os.getenv("DB_USER", current_user)
DB_PASSWORD = os.getenv("DB_PASSWORD", "")  # Empty password by default
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ai_model_eval")

# URL encode username and password to handle special characters
encoded_user = urllib.parse.quote_plus(DB_USER)
encoded_password = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ""

# SQLAlchemy database URL - handle case with or without password
if DB_PASSWORD:
    DATABASE_URL = f"postgresql://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql://{encoded_user}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 