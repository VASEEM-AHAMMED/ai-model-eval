from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Create Base using declarative_base
Base = declarative_base()

class ModelMetadata(Base):
    __tablename__ = 'model_metadata'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    accuracy = Column(Float)
    loss = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    file_path = Column(String, nullable=False)
    format = Column(String, nullable=False)  # csv, json, etc.
    size = Column(Integer)  # number of samples
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSON)  # store additional dataset info
    metrics = relationship("DatasetMetrics", back_populates="dataset")

class DatasetMetrics(Base):
    __tablename__ = "dataset_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.index"))
    model_name = Column(String, nullable=False)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    confusion_matrix = Column(JSON)
    evaluation_date = Column(DateTime(timezone=True), server_default=func.now())
    additional_metrics = Column(JSON)  # store any additional metrics
    
    dataset = relationship("Dataset", back_populates="metrics")
