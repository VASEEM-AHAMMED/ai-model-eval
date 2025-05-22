#!/usr/bin/env python3
"""
Test script for batch uploading datasets to the AI Model Evaluation Platform.
"""

import os
import json
import argparse
import requests
import zipfile
import time
from pathlib import Path

def test_single_upload(api_url, dataset_file, token=None):
    """Test uploading a single dataset file"""
    
    filename = os.path.basename(dataset_file)
    format = filename.split('.')[-1]  # Use file extension as format
    
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    with open(dataset_file, 'rb') as f:
        files = {
            'file': (filename, f),
        }
        
        data = {
            'name': f"Test {filename}",
            'description': f"Test upload of {filename}",
            'format': format
        }
        
        print(f"Uploading {filename}...")
        start_time = time.time()
        
        response = requests.post(
            f"{api_url}/datasets/upload/",
            headers=headers,
            files=files,
            data=data
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful! Dataset ID: {result.get('id')}")
            print(f"   Upload took {duration:.2f} seconds")
            return result
        else:
            print(f"❌ Upload failed! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

def test_batch_upload(api_url, dataset_files, token=None):
    """Test uploading multiple dataset files in one request"""
    
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    files = []
    for i, file_path in enumerate(dataset_files):
        with open(file_path, 'rb') as f:
            files.append(
                ('files', (os.path.basename(file_path), f))
            )
    
    # All files should have the same format for batch upload
    format = dataset_files[0].split('.')[-1]
    
    data = {
        'name_prefix': "Batch Upload Test",
        'description': f"Test batch upload of {len(dataset_files)} files",
        'format': format
    }
    
    print(f"Batch uploading {len(dataset_files)} files...")
    start_time = time.time()
    
    response = requests.post(
        f"{api_url}/datasets/batch-upload",
        headers=headers,
        files=files,
        data=data
    )
    
    duration = time.time() - start_time
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Batch upload successful! Uploaded {len(results)} datasets")
        print(f"   Upload took {duration:.2f} seconds")
        return results
    else:
        print(f"❌ Batch upload failed! Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_zip_upload(api_url, zip_file, token=None):
    """Test uploading a zip file containing multiple datasets"""
    
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    # Determine format based on contents of zip file
    format = "json"  # Default format
    
    with open(zip_file, 'rb') as f:
        files = {
            'zip_file': (os.path.basename(zip_file), f),
        }
        
        data = {
            'name_prefix': "ZIP Upload Test",
            'description': f"Test upload of {zip_file}",
            'format': format
        }
        
        print(f"Uploading ZIP file {zip_file}...")
        start_time = time.time()
        
        response = requests.post(
            f"{api_url}/datasets/upload-zip",
            headers=headers,
            files=files,
            data=data
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ ZIP upload successful! Extracted {len(results)} datasets")
            print(f"   Upload took {duration:.2f} seconds")
            return results
        else:
            print(f"❌ ZIP upload failed! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

def test_upload_with_metrics(api_url, dataset_file, metrics_file, token=None):
    """Test uploading a dataset and then uploading metrics for it"""
    
    # First upload the dataset
    dataset_result = test_single_upload(api_url, dataset_file, token)
    if not dataset_result:
        print("❌ Cannot upload metrics since dataset upload failed")
        return None
    
    dataset_id = dataset_result.get('id')
    
    # Now upload metrics for this dataset
    headers = {
        'Content-Type': 'application/json'
    }
    
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    # Load metrics data
    with open(metrics_file, 'r') as f:
        if metrics_file.endswith('.json'):
            metrics_data = json.load(f)
        elif metrics_file.endswith('.csv'):
            import csv
            csv_reader = csv.DictReader(f)
            metrics_data = list(csv_reader)
    
    # Create sample metrics entries based on the data
    metrics_entries = []
    for i, metric in enumerate(metrics_data[:5]):  # Use first 5 entries
        # Adapt the format based on your metrics schema
        metrics_entries.append({
            "dataset_id": dataset_id,
            "model_name": f"Model {i+1}",
            "accuracy": float(metric.get('accuracy', 0.9)),
            "precision": float(metric.get('precision', 0.85)),
            "recall": float(metric.get('recall', 0.87)),
            "f1_score": float(metric.get('f1_score', 0.86)),
            "latency": [100, 120, 110],
            "timestamps": ["2023-01-01T12:00:00", "2023-01-01T12:30:00", "2023-01-01T13:00:00"],
            "distribution": {"class1": 0.3, "class2": 0.7}
        })
    
    print(f"Uploading metrics for dataset {dataset_id}...")
    start_time = time.time()
    
    response = requests.post(
        f"{api_url}/datasets/{dataset_id}/metrics/batch",
        headers=headers,
        json=metrics_entries
    )
    
    duration = time.time() - start_time
    
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Metrics upload successful! Added {len(results)} metrics entries")
        print(f"   Upload took {duration:.2f} seconds")
        return results
    else:
        print(f"❌ Metrics upload failed! Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def get_auth_token(api_url, username, password):
    """Get authentication token from the API"""
    
    data = {
        'username': username,
        'password': password
    }
    
    response = requests.post(
        f"{api_url}/token",
        data=data
    )
    
    if response.status_code == 200:
        result = response.json()
        return result.get('access_token')
    else:
        print(f"❌ Authentication failed! Status: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Test batch uploads for AI Model Evaluation Platform")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--datasets-dir", default="test_datasets", help="Directory containing test datasets")
    parser.add_argument("--username", default="admin", help="Username for authentication")
    parser.add_argument("--password", default="adminpassword", help="Password for authentication")
    parser.add_argument("--test-type", choices=["single", "batch", "zip", "metrics", "all"], 
                        default="all", help="Type of upload test to run")
    
    args = parser.parse_args()
    
    # Authenticate if credentials provided
    token = None
    if args.username and args.password:
        token = get_auth_token(args.api_url, args.username, args.password)
        if token:
            print(f"✅ Authentication successful")
    
    # Locate test datasets
    datasets_dir = Path(args.datasets_dir)
    if not datasets_dir.exists():
        print(f"❌ Datasets directory {args.datasets_dir} not found")
        return
    
    # Find dataset files
    json_files = list(datasets_dir.glob("*.json"))
    csv_files = list(datasets_dir.glob("*.csv"))
    zip_files = list(datasets_dir.glob("*.zip"))
    
    if not json_files and not csv_files and not zip_files:
        print(f"❌ No dataset files found in {args.datasets_dir}")
        return
    
    # Run the specified tests
    if args.test_type in ("single", "all") and (json_files or csv_files):
        # Test single upload with the first file found
        test_file = json_files[0] if json_files else csv_files[0]
        test_single_upload(args.api_url, str(test_file), token)
        print()
    
    if args.test_type in ("batch", "all") and len(json_files) >= 2:
        # Test batch upload with the first two JSON files
        test_batch_upload(args.api_url, [str(f) for f in json_files[:2]], token)
        print()
    
    if args.test_type in ("zip", "all") and zip_files:
        # Test zip upload with the first zip file
        test_zip_upload(args.api_url, str(zip_files[0]), token)
        print()
    
    if args.test_type in ("metrics", "all") and json_files and csv_files:
        # Test uploading a dataset with metrics
        test_upload_with_metrics(args.api_url, str(json_files[0]), str(csv_files[0]), token)
        print()
    
    print("Testing complete!")

if __name__ == "__main__":
    main() 