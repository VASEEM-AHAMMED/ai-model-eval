#!/usr/bin/env python3
"""
Database management utility for AI Model Evaluation Platform
"""
import argparse
import os
import sys
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Import database components
from db.database import engine, SessionLocal, init_db
from db.models import Dataset, DatasetMetrics

def check_connection():
    """Check if the database connection is working"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            if result and result[0] == 1:
                print(f"✅ Successfully connected to {engine.url.drivername} database!")
                return True
            else:
                print("❌ Connection test failed!")
                return False
    except SQLAlchemyError as e:
        print(f"❌ Database connection error: {e}")
        return False

def list_datasets():
    """List all datasets in the database"""
    db = SessionLocal()
    try:
        datasets = db.query(Dataset).all()
        if not datasets:
            print("No datasets found.")
            return
            
        print(f"Found {len(datasets)} datasets:")
        for ds in datasets:
            print(f"ID: {ds.id} | Name: {ds.name} | Format: {ds.format} | Size: {ds.size or 0} bytes")
    except SQLAlchemyError as e:
        print(f"❌ Error listing datasets: {e}")
    finally:
        db.close()

def list_metrics(dataset_id=None):
    """List metrics, optionally filtered by dataset_id"""
    db = SessionLocal()
    try:
        query = db.query(DatasetMetrics)
        if dataset_id:
            query = query.filter(DatasetMetrics.dataset_id == dataset_id)
            
        metrics = query.all()
        if not metrics:
            filter_msg = f" for dataset ID {dataset_id}" if dataset_id else ""
            print(f"No metrics found{filter_msg}.")
            return
            
        print(f"Found {len(metrics)} metrics:")
        for m in metrics:
            print(f"ID: {m.id} | Dataset: {m.dataset_id} | Model: {m.model_name} | " +
                 f"Accuracy: {m.accuracy or 0:.4f} | F1: {m.f1_score or 0:.4f}")
    except SQLAlchemyError as e:
        print(f"❌ Error listing metrics: {e}")
    finally:
        db.close()

def create_sample_data():
    """Create sample data for testing purposes"""
    db = SessionLocal()
    try:
        # Check if we already have data
        if db.query(Dataset).count() > 0:
            print("Database already contains data. Skipping sample data creation.")
            return
            
        # Create sample datasets
        sample_datasets = [
            Dataset(
                name="Sample Text Classification",
                description="Sample dataset for text classification",
                format="json",
                file_path="samples/text_classification.json",
                size=1024
            ),
            Dataset(
                name="Sample Image Recognition",
                description="Sample dataset for image recognition",
                format="jpg",
                file_path="samples/image_recognition.zip",
                size=2048
            )
        ]
        
        db.add_all(sample_datasets)
        db.flush()  # Flush to get IDs but don't commit yet
        
        # Create sample metrics
        sample_metrics = [
            DatasetMetrics(
                dataset_id=sample_datasets[0].id,
                model_name="BERT-base",
                accuracy=0.92,
                precision=0.89,
                recall=0.94,
                f1_score=0.91,
                latency=[120, 135, 110],
                timestamps=["2023-01-01T12:00:00", "2023-01-01T12:30:00", "2023-01-01T13:00:00"],
                distribution={"class1": 0.3, "class2": 0.7}
            ),
            DatasetMetrics(
                dataset_id=sample_datasets[0].id,
                model_name="RoBERTa",
                accuracy=0.94,
                precision=0.91,
                recall=0.95,
                f1_score=0.93,
                latency=[100, 105, 95],
                timestamps=["2023-01-01T14:00:00", "2023-01-01T14:30:00", "2023-01-01T15:00:00"],
                distribution={"class1": 0.35, "class2": 0.65}
            ),
            DatasetMetrics(
                dataset_id=sample_datasets[1].id,
                model_name="ResNet50",
                accuracy=0.88,
                precision=0.86,
                recall=0.89,
                f1_score=0.87,
                latency=[200, 210, 195],
                timestamps=["2023-01-02T12:00:00", "2023-01-02T12:30:00", "2023-01-02T13:00:00"],
                distribution={"cat": 0.4, "dog": 0.6}
            )
        ]
        
        db.add_all(sample_metrics)
        db.commit()
        print("✅ Sample data created successfully.")
        
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
    finally:
        db.close()

def main():
    """Main function to parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description='Database management for AI Model Evaluation Platform')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Check connection command
    subparsers.add_parser('check', help='Check database connection')
    
    # List datasets command
    subparsers.add_parser('list-datasets', help='List all datasets')
    
    # List metrics command
    metrics_parser = subparsers.add_parser('list-metrics', help='List metrics')
    metrics_parser.add_argument('--dataset-id', type=int, help='Filter metrics by dataset ID')
    
    # Initialize database command
    subparsers.add_parser('init', help='Initialize database schema')
    
    # Create sample data command
    sample_parser = subparsers.add_parser('create-samples', help='Create sample data')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        check_connection()
    elif args.command == 'list-datasets':
        list_datasets()
    elif args.command == 'list-metrics':
        list_metrics(args.dataset_id)
    elif args.command == 'init':
        init_db()
        print("✅ Database schema initialized.")
    elif args.command == 'create-samples':
        create_sample_data()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 