from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# Dataset Schemas
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    format: str

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: int
    file_path: str
    size: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Metrics Schemas
class MetricsBase(BaseModel):
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    latency: Optional[List[float]] = None
    timestamps: Optional[List[str]] = None
    distribution: Optional[Dict[str, Any]] = None

class MetricsCreate(MetricsBase):
    dataset_id: int

class Metrics(MetricsBase):
    id: int
    dataset_id: int
    created_at: datetime

    class Config:
        from_attributes = True 