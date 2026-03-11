"""
SQLAlchemy database models for FRS Data Management System.
Defines the schema for datasets, units, and sheet data.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Dataset(Base):
    """
    Represents a collection of FRS data uploaded with a specific tag.
    """
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(255), unique=True, nullable=False, index=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    month_label = Column(String(50))  # e.g., "November", "December"
    description = Column(Text)
    
    # Relationships
    units = relationship("Unit", back_populates="dataset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, tag='{self.tag}', month='{self.month_label}')>"


class Unit(Base):
    """
    Represents a military formation unit (e.g., Fmn A, Fmn B) within a dataset.
    """
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    unit_name = Column(String(100), nullable=False)  # e.g., "Fmn A", "Fmn B"
    file_path = Column(Text)  # Original file path for reference
    
    # Relationships
    dataset = relationship("Dataset", back_populates="units")
    sheet_data = relationship("SheetData", back_populates="unit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Unit(id={self.id}, name='{self.unit_name}', dataset_id={self.dataset_id})>"


class SheetData(Base):
    """
    Represents data from a single Excel sheet within a unit's file.
    Uses JSONB for flexible schema to accommodate different sheet structures.
    """
    __tablename__ = "sheet_data"
    
    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False)
    sheet_type = Column(String(50), nullable=False, index=True)  # e.g., "APPX_A_BVEH", "ARMT"
    row_data = Column(JSON, nullable=False)  # Array of row objects with column data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    unit = relationship("Unit", back_populates="sheet_data")
    
    def __repr__(self):
        return f"<SheetData(id={self.id}, unit_id={self.unit_id}, sheet_type='{self.sheet_type}')>"
