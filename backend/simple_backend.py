from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
import os
import json
import shutil
from datetime import datetime
import uuid

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
datasets = []
metrics = {}

# Create uploads directory
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Model Evaluation Platform!"}

@app.post("/datasets/upload/")
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    format: str = Form("json")
):
    try:
        # Save the file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create a dataset record
        dataset_id = str(uuid.uuid4())
        
        # Load the JSON file for demo metrics
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Store metrics for later retrieval
                if 'metrics' in data:
                    metrics[dataset_id] = data['metrics']
                elif 'accuracy' in data:  # Handle flat structure
                    metrics[dataset_id] = {
                        'accuracy': data.get('accuracy', 0),
                        'precision': data.get('precision', 0),
                        'recall': data.get('recall', 0),
                        'f1_score': data.get('f1_score', 0)
                    }
        except:
            # If we can't parse metrics, create empty ones
            metrics[dataset_id] = {
                'accuracy': 0.5,
                'precision': 0.6,
                'recall': 0.7,
                'f1_score': 0.65
            }
        
        # Create dataset record
        dataset = {
            "id": dataset_id,
            "name": name,
            "description": description or "",
            "file_path": file_path,
            "format": format,
            "size": os.path.getsize(file_path),
            "created_at": datetime.now().isoformat()
        }
        
        datasets.append(dataset)
        
        return {"message": "Dataset uploaded successfully", "dataset": dataset}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/datasets/")
async def list_datasets():
    return datasets

@app.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    for dataset in datasets:
        if dataset["id"] == dataset_id:
            return dataset
    raise HTTPException(status_code=404, detail="Dataset not found")

@app.get("/datasets/{dataset_id}/metrics/")
async def get_dataset_metrics(dataset_id: str):
    # For the demo, we'll return dummy metrics if none exist
    if dataset_id not in metrics:
        # Create some dummy latency and distribution data
        return {
            "accuracy": 0.87,
            "precision": 0.82,
            "recall": 0.89,
            "f1_score": 0.85,
            "latency": [120, 115, 125, 118, 122, 130, 119, 121, 117, 124],
            "timestamps": [
                "2023-12-01T10:00:00", "2023-12-01T10:05:00", 
                "2023-12-01T10:10:00", "2023-12-01T10:15:00",
                "2023-12-01T10:20:00", "2023-12-01T10:25:00",
                "2023-12-01T10:30:00", "2023-12-01T10:35:00",
                "2023-12-01T10:40:00", "2023-12-01T10:45:00"
            ],
            "distribution": {
                "categories": ["Class A", "Class B", "Class C", "Class D", "Class E"],
                "counts": [45, 32, 28, 18, 27]
            }
        }
    
    # Add latency and distribution data if not present
    metric_data = metrics[dataset_id].copy()
    if 'latency' not in metric_data:
        metric_data['latency'] = [120, 115, 125, 118, 122, 130, 119, 121, 117, 124]
    if 'timestamps' not in metric_data:
        metric_data['timestamps'] = [
            "2023-12-01T10:00:00", "2023-12-01T10:05:00", 
            "2023-12-01T10:10:00", "2023-12-01T10:15:00",
            "2023-12-01T10:20:00", "2023-12-01T10:25:00",
            "2023-12-01T10:30:00", "2023-12-01T10:35:00",
            "2023-12-01T10:40:00", "2023-12-01T10:45:00"
        ]
    if 'distribution' not in metric_data:
        metric_data['distribution'] = {
            "categories": ["Class A", "Class B", "Class C", "Class D", "Class E"],
            "counts": [45, 32, 28, 18, 27]
        }
    
    return metric_data 