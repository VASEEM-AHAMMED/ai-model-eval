"""
Database reset utility for AI Model Evaluation Platform.
For development purposes only.
"""

import os
import sys
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db.database import engine, init_db

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    try:
        # Try to connect to the database
        with engine.connect() as conn:
            print("Connected to database.")
            
            # Check if we're using SQLite or PostgreSQL
            if engine.dialect.name == 'sqlite':
                # For SQLite we can just drop all tables and recreate them
                from db.models import Base
                print("Dropping all tables...")
                Base.metadata.drop_all(bind=engine)
                print("Recreating all tables...")
                Base.metadata.create_all(bind=engine)
            else:
                # For PostgreSQL, we can use a more powerful approach
                # WARNING: This will delete all data in the tables
                print("Resetting all tables in PostgreSQL...")
                conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                    text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
                )
                
                # Reset sequence IDs - might be needed depending on your setup
                conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
                
                # Reinitialize the database with empty tables
                init_db()
                
            print("✅ Database has been reset successfully.")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database reset failed: {e}")
        return False
        
if __name__ == "__main__":
    # Confirm with the user before proceeding
    confirm = input("This will DELETE ALL DATA in the database. Type 'yes' to confirm: ")
    
    if confirm.lower() == 'yes':
        success = reset_database()
        if success:
            print("Database reset complete.")
        else:
            print("Database reset failed.")
            sys.exit(1)
    else:
        print("Database reset cancelled.") 