"""
Pydantic schemas for data validation
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


# Dataset schemas
class DatasetBase(BaseModel):
    """Base schema for Dataset"""
    name: str
    description: Optional[str] = None
    format: str


class DatasetCreate(DatasetBase):
    """Schema for creating a Dataset"""
    pass


class DatasetUpdate(BaseModel):
    """Schema for updating a Dataset"""
    name: Optional[str] = None
    description: Optional[str] = None
    format: Optional[str] = None


class DatasetInDB(DatasetBase):
    """Schema for Dataset as stored in the database"""
    id: int
    file_path: str
    size: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DatasetRead(DatasetInDB):
    """Schema for reading a Dataset"""
    pass


# Metrics schemas
class MetricsBase(BaseModel):
    """Base schema for Metrics"""
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    latency: Optional[List[float]] = None
    timestamps: Optional[List[str]] = None
    distribution: Optional[Dict[str, Any]] = None


class MetricsCreate(MetricsBase):
    """Schema for creating Metrics"""
    dataset_id: int


class MetricsUpdate(BaseModel):
    """Schema for updating Metrics"""
    model_name: Optional[str] = None
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    latency: Optional[List[float]] = None
    timestamps: Optional[List[str]] = None
    distribution: Optional[Dict[str, Any]] = None


class MetricsInDB(MetricsBase):
    """Schema for Metrics as stored in the database"""
    id: int
    dataset_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MetricsRead(MetricsInDB):
    """Schema for reading Metrics"""
    pass 