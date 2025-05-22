"""
Visualization utilities for AI Model Evaluation Platform.
These functions generate data for visualizations to be used by the frontend.
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.models import Dataset, DatasetMetrics


def get_accuracy_comparison(db: Session, dataset_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get accuracy comparison data for visualizations
    
    Args:
        db: Database session
        dataset_id: Optional dataset ID to filter data
        
    Returns:
        Dictionary with model names and their accuracy metrics
    """
    query = db.query(DatasetMetrics.model_name, 
                    DatasetMetrics.accuracy, 
                    DatasetMetrics.precision,
                    DatasetMetrics.recall,
                    DatasetMetrics.f1_score)
    
    if dataset_id:
        query = query.filter(DatasetMetrics.dataset_id == dataset_id)
    
    metrics = query.all()
    
    # Prepare visualization data
    result = {
        "models": [],
        "accuracy": [],
        "precision": [],
        "recall": [],
        "f1_score": []
    }
    
    for metric in metrics:
        result["models"].append(metric.model_name)
        result["accuracy"].append(metric.accuracy if metric.accuracy is not None else 0)
        result["precision"].append(metric.precision if metric.precision is not None else 0)
        result["recall"].append(metric.recall if metric.recall is not None else 0)
        result["f1_score"].append(metric.f1_score if metric.f1_score is not None else 0)
    
    return result


def get_latency_data(db: Session, dataset_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get latency data for visualizations
    
    Args:
        db: Database session
        dataset_id: Optional dataset ID to filter data
        
    Returns:
        Dictionary with model names and their latency data
    """
    query = db.query(DatasetMetrics.model_name, DatasetMetrics.latency, DatasetMetrics.timestamps)
    
    if dataset_id:
        query = query.filter(DatasetMetrics.dataset_id == dataset_id)
    
    metrics = query.all()
    
    # Prepare visualization data
    result = {}
    
    for metric in metrics:
        if not metric.latency or not metric.timestamps:
            continue
            
        model_name = metric.model_name
        latency = metric.latency
        timestamps = metric.timestamps
        
        if model_name not in result:
            result[model_name] = {"timestamps": [], "latency": []}
            
        result[model_name]["timestamps"].extend(timestamps)
        result[model_name]["latency"].extend(latency)
    
    return result


def get_distribution_chart_data(db: Session, dataset_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get distribution data for visualizations
    
    Args:
        db: Database session
        dataset_id: Optional dataset ID to filter data
        
    Returns:
        Dictionary with distribution data for charts
    """
    query = db.query(DatasetMetrics.model_name, DatasetMetrics.distribution)
    
    if dataset_id:
        query = query.filter(DatasetMetrics.dataset_id == dataset_id)
    
    metrics = query.all()
    
    # Prepare visualization data
    result = {}
    
    for metric in metrics:
        if not metric.distribution:
            continue
            
        model_name = metric.model_name
        distribution = metric.distribution
        
        if not isinstance(distribution, dict):
            distribution = json.loads(distribution)
            
        result[model_name] = distribution
    
    return result


def get_models_over_time(db: Session) -> Dict[str, Any]:
    """
    Get model performance over time
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with model performance over time
    """
    from sqlalchemy import extract, func
    from datetime import datetime
    
    # Get year-month from created_at
    metrics = db.query(
        func.date_trunc('month', DatasetMetrics.created_at).label('month'),
        func.count(DatasetMetrics.id).label('count'),
        func.avg(DatasetMetrics.accuracy).label('avg_accuracy')
    ).group_by(
        func.date_trunc('month', DatasetMetrics.created_at)
    ).order_by(
        func.date_trunc('month', DatasetMetrics.created_at)
    ).all()
    
    # Prepare visualization data
    result = {
        "timeline": [],
        "count": [],
        "avg_accuracy": []
    }
    
    for metric in metrics:
        if metric.month:
            result["timeline"].append(metric.month.strftime("%Y-%m"))
            result["count"].append(metric.count)
            result["avg_accuracy"].append(
                float(metric.avg_accuracy) if metric.avg_accuracy else 0.0
            )
    
    return result 