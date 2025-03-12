from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

# Create Base using declarative_base
Base = declarative_base()

class ModelMetadata(Base):
    __tablename__ = 'model_metadata'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    accuracy = Column(Float)
    loss = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
