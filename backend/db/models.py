"""
Database models for AI Model Evaluation Platform
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base


class Dataset(Base):
    """Dataset model for storing dataset information"""
    
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    file_path = Column(String, nullable=False)
    format = Column(String, nullable=False)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with metrics
    metrics = relationship("DatasetMetrics", back_populates="dataset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}', format='{self.format}')>"


class DatasetMetrics(Base):
    """Metrics model for storing model evaluation metrics"""
    
    __tablename__ = "dataset_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    model_name = Column(String, nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    latency = Column(JSON, nullable=True)  # Stored as JSON array
    timestamps = Column(JSON, nullable=True)  # Stored as JSON array
    distribution = Column(JSON, nullable=True)  # Stored as JSON object
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with dataset
    dataset = relationship("Dataset", back_populates="metrics")
    
    def __repr__(self):
        return f"<DatasetMetrics(id={self.id}, model_name='{self.model_name}', dataset_id={self.dataset_id})>" 