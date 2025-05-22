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

# Import database components
from db.database import engine, get_db, init_db
from db.models import Dataset, DatasetMetrics

def check_connection():
    """Check database connection and print status"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"✅ Database connection successful! Result: {result}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def list_datasets():
    """List all datasets in the database"""
    db = next(get_db())
    try:
        datasets = db.query(Dataset).all()
        if not datasets:
            print("No datasets found.")
            return
        
        print(f"Found {len(datasets)} datasets:")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<30} {'Format':<10} {'Size':<10} {'Created At':<25}")
        print("-" * 80)
        for dataset in datasets:
            print(f"{dataset.id:<5} {dataset.name:<30} {dataset.format:<10} {dataset.size:<10} {dataset.created_at}")
    finally:
        db.close()

def list_metrics(dataset_id=None):
    """List metrics for a specific dataset or all metrics"""
    db = next(get_db())
    try:
        query = db.query(DatasetMetrics)
        if dataset_id:
            query = query.filter(DatasetMetrics.dataset_id == dataset_id)
        
        metrics = query.all()
        if not metrics:
            print(f"No metrics found{' for dataset ' + str(dataset_id) if dataset_id else ''}.")
            return
        
        print(f"Found {len(metrics)} metrics:")
        print("-" * 100)
        print(f"{'ID':<5} {'Dataset ID':<10} {'Model':<20} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1':<10}")
        print("-" * 100)
        for metric in metrics:
            print(f"{metric.id:<5} {metric.dataset_id:<10} {metric.model_name:<20} {metric.accuracy or 'N/A':<10} {metric.precision or 'N/A':<10} {metric.recall or 'N/A':<10} {metric.f1_score or 'N/A':<10}")
    finally:
        db.close()

def init_database():
    """Initialize the database schema"""
    try:
        init_db()
        print("✅ Database schema created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        return False

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
    
    args = parser.parse_args()
    
    if args.command == 'check':
        check_connection()
    elif args.command == 'list-datasets':
        list_datasets()
    elif args.command == 'list-metrics':
        list_metrics(args.dataset_id)
    elif args.command == 'init':
        init_database()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 