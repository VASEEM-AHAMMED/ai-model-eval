"""
Data export functionality for AI Model Evaluation Platform.
Supports exporting datasets and metrics to various formats.
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from fastapi.responses import FileResponse, StreamingResponse
from io import StringIO

from db.models import Dataset, DatasetMetrics

# Make pandas optional, only needed for certain advanced features
pandas_available = False
try:
    import pandas as pd
    pandas_available = True
except ImportError:
    pass


def fix_csv_formatting(content: bytes) -> Tuple[bytes, bool]:
    """
    Attempt to fix common CSV formatting issues
    
    Args:
        content: Raw CSV file content
        
    Returns:
        Tuple of (fixed content, whether changes were made)
    """
    try:
        # Decode content
        decoded = content.decode('utf-8', errors='replace')
        
        # Check for and fix common issues
        fixed = decoded
        
        # Replace inconsistent line endings
        original_lines = fixed.splitlines()
        fixed = '\n'.join(original_lines)
        
        # Fix missing quotes around fields with commas
        if pandas_available:
            try:
                # Try to use pandas for more robust CSV parsing and fixing
                buffer = StringIO(fixed)
                df = pd.read_csv(buffer, engine='python', error_bad_lines=False)
                output = StringIO()
                df.to_csv(output, index=False)
                fixed = output.getvalue()
            except Exception:
                # If pandas fails, continue with the basic fixes
                pass
        
        # Check if we made any changes
        changes_made = fixed != decoded
        
        return fixed.encode('utf-8'), changes_made
    except Exception:
        # If anything fails, return the original content
        return content, False


def export_dataset_to_json(dataset: Dataset, metrics: List[DatasetMetrics]) -> str:
    """
    Export a dataset and its metrics to JSON format
    
    Args:
        dataset: Dataset object
        metrics: List of DatasetMetrics objects
        
    Returns:
        JSON string representation of the dataset and metrics
    """
    # Base dataset info
    result = {
        "dataset": {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "format": dataset.format,
            "size": dataset.size,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None
        },
        "metrics": []
    }
    
    # Add metrics data
    for metric in metrics:
        metric_dict = {
            "id": metric.id,
            "model_name": metric.model_name,
            "accuracy": metric.accuracy,
            "precision": metric.precision,
            "recall": metric.recall,
            "f1_score": metric.f1_score,
            "latency": metric.latency,
            "timestamps": metric.timestamps,
            "distribution": metric.distribution,
            "created_at": metric.created_at.isoformat() if metric.created_at else None
        }
        result["metrics"].append(metric_dict)
    
    return json.dumps(result, indent=2)


def export_metrics_to_csv(metrics: List[DatasetMetrics]) -> str:
    """
    Export metrics to CSV format
    
    Args:
        metrics: List of DatasetMetrics objects
        
    Returns:
        CSV string representation of the metrics
    """
    if not metrics:
        return ""
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "id", "dataset_id", "model_name", "accuracy", "precision", 
        "recall", "f1_score", "created_at"
    ])
    
    # Write data rows
    for metric in metrics:
        writer.writerow([
            metric.id, metric.dataset_id, metric.model_name,
            metric.accuracy, metric.precision, metric.recall,
            metric.f1_score, 
            metric.created_at.isoformat() if metric.created_at else None
        ])
    
    return output.getvalue()


def create_export_file(content: str, filename: str, export_dir: str = "exports") -> str:
    """
    Create an export file with the given content
    
    Args:
        content: String content to write to file
        filename: Name of the export file
        export_dir: Directory to store exports (created if not exists)
        
    Returns:
        Path to the created file
    """
    # Create exports directory if doesn't exist
    os.makedirs(export_dir, exist_ok=True)
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{filename}"
    file_path = os.path.join(export_dir, filename)
    
    # Write content to file
    with open(file_path, "w") as f:
        f.write(content)
    
    return file_path 