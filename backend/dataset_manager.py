import os
import json
import pandas as pd
from typing import Optional, Dict, Any
from fastapi import UploadFile
from models import Dataset, DatasetMetrics
from database import SessionLocal
import shutil

class DatasetManager:
    def __init__(self):
        self.upload_dir = "data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_uploaded_file(self, file: UploadFile) -> str:
        """Save an uploaded file and return its path"""
        file_path = os.path.join(self.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path

    async def create_dataset(
        self,
        file: UploadFile,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dataset:
        """Create a new dataset entry"""
        file_path = await self.save_uploaded_file(file)
        
        # Determine format and size
        format = file.filename.split('.')[-1].lower()
        size = await self._get_dataset_size(file_path, format)
        
        db = SessionLocal()
        try:
            dataset = Dataset(
                name=name,
                description=description,
                file_path=file_path,
                format=format,
                size=size,
                metadata=metadata or {}
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            return dataset
        finally:
            db.close()

    async def _get_dataset_size(self, file_path: str, format: str) -> int:
        """Get the number of samples in the dataset"""
        if format == 'csv':
            return len(pd.read_csv(file_path))
        elif format == 'json':
            with open(file_path, 'r') as f:
                data = json.load(f)
                return len(data)
        return 0

    async def get_dataset(self, dataset_id: int) -> Optional[Dataset]:
        """Retrieve a dataset by ID"""
        db = SessionLocal()
        try:
            return db.query(Dataset).filter(Dataset.id == dataset_id).first()
        finally:
            db.close()

    async def save_metrics(
        self,
        dataset_id: int,
        model_name: str,
        metrics: Dict[str, Any]
    ) -> DatasetMetrics:
        """Save evaluation metrics for a dataset"""
        db = SessionLocal()
        try:
            dataset_metrics = DatasetMetrics(
                dataset_id=dataset_id,
                model_name=model_name,
                accuracy=metrics.get('accuracy'),
                precision=metrics.get('precision'),
                recall=metrics.get('recall'),
                f1_score=metrics.get('f1_score'),
                confusion_matrix=metrics.get('confusion_matrix'),
                additional_metrics=metrics.get('additional_metrics', {})
            )
            db.add(dataset_metrics)
            db.commit()
            db.refresh(dataset_metrics)
            return dataset_metrics
        finally:
            db.close()

    async def get_dataset_metrics(self, dataset_id: int) -> list[DatasetMetrics]:
        """Get all metrics for a dataset"""
        db = SessionLocal()
        try:
            return db.query(DatasetMetrics).filter(
                DatasetMetrics.dataset_id == dataset_id
            ).all()
        finally:
            db.close() 