import os
import sys
from sqlalchemy import create_engine, text

# Get current username
current_user = os.environ.get("USER", "vaseem")  # Default to 'vaseem' if USER env var not set
print(f"Current user: {current_user}")

# PostgreSQL connection URL
DATABASE_URL = f"postgresql://{current_user}@localhost:5432/ai_model_eval"
print(f"Attempting to connect to: {DATABASE_URL}")

try:
    # Create engine and test connection
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Connection successful! Result: {result.scalar()}")
    
    print("Connected to PostgreSQL database!")
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")
    sys.exit(1)

print("Connection test complete.") 