import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Import models from main.py
from main import Dataset, DatasetMetrics, Base

# Try PostgreSQL first, then fall back to SQLite
try:
    # Try PostgreSQL connection
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ai_model_eval"
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Connected to PostgreSQL database!")
except Exception as e:
    print(f"❌ PostgreSQL connection failed: {e}")
    print("Falling back to SQLite database")
    
    # Fallback to SQLite
    DATABASE_URL = "sqlite:///./ai_model_eval.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ Connected to SQLite database!")

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Ensure tables exist
print("Creating tables if they don't exist...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created or already exist")

# Test CRUD operations
try:
    print("\n--- Testing CRUD operations ---")
    
    # 1. Create a test dataset
    print("Creating test dataset...")
    test_dataset = Dataset(
        name="Test Dataset",
        description="A test dataset for database verification",
        file_path="test/path/to/file.csv",
        format="csv",
        size=1024
    )
    db.add(test_dataset)
    db.commit()
    db.refresh(test_dataset)
    print(f"✅ Created dataset with ID: {test_dataset.id}")
    
    # 2. Create test metrics
    print("Creating test metrics...")
    test_metrics = DatasetMetrics(
        dataset_id=test_dataset.id,
        model_name="Test Model",
        accuracy=0.95,
        precision=0.92,
        recall=0.91,
        f1_score=0.93,
        latency=[120, 115, 125],
        timestamps=["2023-12-01T10:00:00", "2023-12-01T10:05:00", "2023-12-01T10:10:00"],
        distribution={"categories": ["Class A", "Class B"], "counts": [45, 32]}
    )
    db.add(test_metrics)
    db.commit()
    db.refresh(test_metrics)
    print(f"✅ Created metrics with ID: {test_metrics.id}")
    
    # 3. Read data
    print("Reading data from database...")
    retrieved_dataset = db.query(Dataset).filter(Dataset.id == test_dataset.id).first()
    print(f"✅ Retrieved dataset: {retrieved_dataset.name}")
    
    retrieved_metrics = db.query(DatasetMetrics).filter(DatasetMetrics.id == test_metrics.id).first()
    print(f"✅ Retrieved metrics with accuracy: {retrieved_metrics.accuracy}")
    
    # 4. Update data
    print("Updating dataset...")
    retrieved_dataset.description = "Updated description"
    db.commit()
    db.refresh(retrieved_dataset)
    print(f"✅ Updated dataset description: {retrieved_dataset.description}")
    
    # 5. Delete test data (cleanup)
    print("Cleaning up test data...")
    db.delete(retrieved_metrics)
    db.delete(retrieved_dataset)
    db.commit()
    print("✅ Test data deleted")
    
    print("\n✅ All database operations completed successfully!")
    
except Exception as e:
    print(f"❌ Error during database operations: {e}")
    db.rollback()
finally:
    db.close() 