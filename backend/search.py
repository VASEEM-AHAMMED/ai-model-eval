"""
Search and filtering functionality for AI Model Evaluation Platform.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from db.models import Dataset, DatasetMetrics


def search_datasets(db: Session, query: str = None, sort_by: str = "created_at", 
                   sort_dir: str = "desc", limit: int = 100, 
                   offset: int = 0, **filters) -> List[Dataset]:
    """
    Search datasets with filtering and sorting capabilities
    
    Args:
        db: Database session
        query: Text search query
        sort_by: Field to sort by (default: created_at)
        sort_dir: Sort direction - "asc" or "desc" (default: desc)
        limit: Maximum number of results
        offset: Offset for pagination
        **filters: Additional field filters
        
    Returns:
        List of Dataset objects matching the criteria
    """
    # Start with base query
    dataset_query = db.query(Dataset)
    
    # Apply text search if provided
    if query:
        # Search in name and description
        dataset_query = dataset_query.filter(
            or_(
                Dataset.name.ilike(f"%{query}%"),
                Dataset.description.ilike(f"%{query}%")
            )
        )
    
    # Apply additional filters
    if "format" in filters and filters["format"]:
        dataset_query = dataset_query.filter(Dataset.format == filters["format"])
        
    if "min_size" in filters and filters["min_size"]:
        dataset_query = dataset_query.filter(Dataset.size >= filters["min_size"])
        
    if "max_size" in filters and filters["max_size"]:
        dataset_query = dataset_query.filter(Dataset.size <= filters["max_size"])
    
    # Apply sorting
    if sort_dir.lower() == "asc":
        dataset_query = dataset_query.order_by(asc(getattr(Dataset, sort_by)))
    else:
        dataset_query = dataset_query.order_by(desc(getattr(Dataset, sort_by)))
    
    # Apply pagination
    return dataset_query.offset(offset).limit(limit).all()


def search_metrics(db: Session, dataset_id: Optional[int] = None, 
                  model_name: Optional[str] = None, min_accuracy: Optional[float] = None,
                  min_f1: Optional[float] = None, sort_by: str = "created_at",
                  sort_dir: str = "desc", limit: int = 100, 
                  offset: int = 0) -> List[DatasetMetrics]:
    """
    Search metrics with filtering and sorting capabilities
    
    Args:
        db: Database session
        dataset_id: Filter by dataset ID
        model_name: Filter by model name
        min_accuracy: Filter by minimum accuracy
        min_f1: Filter by minimum F1 score
        sort_by: Field to sort by 
        sort_dir: Sort direction - "asc" or "desc"
        limit: Maximum number of results
        offset: Offset for pagination
        
    Returns:
        List of DatasetMetrics objects matching the criteria
    """
    # Start with base query
    metrics_query = db.query(DatasetMetrics)
    
    # Apply filters
    if dataset_id:
        metrics_query = metrics_query.filter(DatasetMetrics.dataset_id == dataset_id)
    
    if model_name:
        metrics_query = metrics_query.filter(DatasetMetrics.model_name.ilike(f"%{model_name}%"))
    
    if min_accuracy is not None:
        metrics_query = metrics_query.filter(DatasetMetrics.accuracy >= min_accuracy)
        
    if min_f1 is not None:
        metrics_query = metrics_query.filter(DatasetMetrics.f1_score >= min_f1)
    
    # Apply sorting
    if sort_dir.lower() == "asc":
        metrics_query = metrics_query.order_by(asc(getattr(DatasetMetrics, sort_by)))
    else:
        metrics_query = metrics_query.order_by(desc(getattr(DatasetMetrics, sort_by)))
    
    # Apply pagination
    return metrics_query.offset(offset).limit(limit).all()


def get_metrics_summary(db: Session, dataset_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get summary statistics for metrics
    
    Args:
        db: Database session
        dataset_id: Optional dataset ID to filter metrics
        
    Returns:
        Dictionary with summary statistics
    """
    from sqlalchemy import func
    
    # Base query
    query = db.query(
        func.avg(DatasetMetrics.accuracy).label('avg_accuracy'),
        func.avg(DatasetMetrics.precision).label('avg_precision'),
        func.avg(DatasetMetrics.recall).label('avg_recall'),
        func.avg(DatasetMetrics.f1_score).label('avg_f1'),
        func.count(DatasetMetrics.id).label('count')
    )
    
    # Apply dataset filter if provided
    if dataset_id:
        query = query.filter(DatasetMetrics.dataset_id == dataset_id)
    
    # Execute query
    result = query.first()
    
    # Construct summary dict
    return {
        "count": result.count if result else 0,
        "accuracy": {
            "avg": float(result.avg_accuracy) if result and result.avg_accuracy else 0.0
        },
        "precision": {
            "avg": float(result.avg_precision) if result and result.avg_precision else 0.0
        },
        "recall": {
            "avg": float(result.avg_recall) if result and result.avg_recall else 0.0
        },
        "f1_score": {
            "avg": float(result.avg_f1) if result and result.avg_f1 else 0.0
        }
    } 