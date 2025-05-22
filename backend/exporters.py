"""
Data export functionality for AI Model Evaluation Platform.
Supports exporting datasets and metrics to various formats.
"""

import os
import json
import csv
import re
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from fastapi.responses import FileResponse, StreamingResponse
from io import StringIO, BytesIO

from db.models import Dataset, DatasetMetrics

# Make pandas optional, only needed for certain advanced features
pandas_available = False
try:
    import pandas as pd
    pandas_available = True
except ImportError:
    pass


def diagnose_csv_issues(content: bytes) -> Dict[str, Any]:
    """
    Perform detailed diagnosis of CSV formatting issues
    
    Args:
        content: Raw CSV file content
        
    Returns:
        Dictionary with diagnostic information
    """
    issues = {
        "has_issues": False,
        "diagnostic": [],
        "fixable": True,
        "detected_encoding": "utf-8",
        "line_ending_issues": False,
        "quoting_issues": False,
        "column_count_mismatch": False,
        "empty_file": False,
        "invalid_characters": False
    }
    
    # Check if file is empty
    if not content or len(content) == 0:
        issues["has_issues"] = True
        issues["diagnostic"].append("File is empty")
        issues["empty_file"] = True
        issues["fixable"] = False
        return issues
    
    # Try to detect encoding
    encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
    content_decoded = None
    
    for encoding in encodings:
        try:
            content_decoded = content.decode(encoding)
            issues["detected_encoding"] = encoding
            break
        except UnicodeDecodeError:
            continue
    
    if not content_decoded:
        issues["has_issues"] = True
        issues["diagnostic"].append("Unable to determine file encoding")
        issues["fixable"] = False
        return issues
    
    # Check line endings
    if "\r\n" in content_decoded and "\n" in content_decoded.replace("\r\n", ""):
        issues["has_issues"] = True
        issues["diagnostic"].append("Mixed line endings (\\r\\n and \\n)")
        issues["line_ending_issues"] = True
    
    # Check for invalid characters
    if re.search(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', content_decoded):
        issues["has_issues"] = True
        issues["diagnostic"].append("Contains invalid control characters")
        issues["invalid_characters"] = True
    
    try:
        # Parse the CSV to look for more issues
        rows = list(csv.reader(StringIO(content_decoded)))
        
        if len(rows) == 0:
            issues["has_issues"] = True
            issues["diagnostic"].append("No CSV rows detected")
            issues["empty_file"] = True
            return issues
        
        # Check column counts
        first_row_cols = len(rows[0])
        for i, row in enumerate(rows[1:], 2):
            if len(row) != first_row_cols:
                issues["has_issues"] = True
                issues["diagnostic"].append(f"Row {i} has {len(row)} columns, expected {first_row_cols}")
                issues["column_count_mismatch"] = True
                break
        
        # Check for quoting issues by looking for commas in fields
        for row in rows:
            for field in row:
                if ',' in field and not (field.startswith('"') and field.endswith('"')):
                    issues["has_issues"] = True
                    issues["diagnostic"].append("Detected unquoted fields containing commas")
                    issues["quoting_issues"] = True
                    break
            if issues["quoting_issues"]:
                break
                
    except Exception as e:
        issues["has_issues"] = True
        issues["diagnostic"].append(f"CSV parsing error: {str(e)}")
        # Some errors might not be fixable
        if "newline character seen" in str(e) or "line contains NUL" in str(e):
            issues["fixable"] = False
    
    return issues


def fix_csv_formatting(content: bytes, return_diagnostic: bool = False) -> Tuple[bytes, bool, Optional[Dict]]:
    """
    Attempt to fix common CSV formatting issues
    
    Args:
        content: Raw CSV file content
        return_diagnostic: Whether to return detailed diagnostic information
        
    Returns:
        Tuple of (fixed content, whether changes were made, diagnostic info if requested)
    """
    # Get detailed diagnostic information
    diagnostic = diagnose_csv_issues(content)
    
    # If issues aren't fixable, return original content
    if diagnostic["has_issues"] and not diagnostic["fixable"]:
        if return_diagnostic:
            return content, False, diagnostic
        return content, False
    
    try:
        # Decode content with appropriate encoding
        decoded = content.decode(diagnostic["detected_encoding"], errors='replace')
        
        # Fix line endings
        original_lines = decoded.splitlines()
        fixed = '\n'.join(original_lines)
        
        # Remove invalid control characters
        if diagnostic["invalid_characters"]:
            fixed = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', fixed)
        
        # Try advanced fixes with pandas if available
        if pandas_available and (diagnostic["column_count_mismatch"] or diagnostic["quoting_issues"]):
            try:
                buffer = StringIO(fixed)
                # Use more tolerant pandas options
                df = pd.read_csv(
                    buffer, 
                    engine='python',
                    error_bad_lines=False,
                    warn_bad_lines=False,
                    on_bad_lines='skip',
                    encoding_errors='ignore',
                    quotechar='"',
                    escapechar='\\'
                )
                
                # If we got to here, pandas managed to read it - output with correct formatting
                output = StringIO()
                df.to_csv(output, index=False, quoting=csv.QUOTE_NONNUMERIC)
                fixed = output.getvalue()
            except Exception as e:
                # If pandas fails, continue with the basic fixes we've already applied
                diagnostic["diagnostic"].append(f"Pandas fix failed: {str(e)}")
                pass
        
        # Check if we made any changes
        changes_made = fixed != decoded
        
        result = fixed.encode('utf-8')
        
        if return_diagnostic:
            return result, changes_made, diagnostic
        return result, changes_made
        
    except Exception as e:
        tb = traceback.format_exc()
        diagnostic["has_issues"] = True
        diagnostic["fixable"] = False
        diagnostic["diagnostic"].append(f"Exception during fix: {str(e)}")
        diagnostic["diagnostic"].append(tb)
        
        if return_diagnostic:
            return content, False, diagnostic
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