"""
Pydantic schemas for request/response validation in FRS Data Management System.
Provides data validation and serialization for API endpoints.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ============ Dataset Schemas ============

class DatasetBase(BaseModel):
    """Base schema for Dataset"""
    tag: str = Field(..., description="Unique identifier/tag for the dataset")
    month_label: Optional[str] = Field(None, description="Month label (e.g., 'November', 'December')")
    description: Optional[str] = Field(None, description="Optional description")


class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset"""
    pass


class DatasetResponse(DatasetBase):
    """Schema for dataset response"""
    id: int
    upload_date: datetime
    unit_count: Optional[int] = Field(None, description="Number of units in this dataset")
    
    class Config:
        from_attributes = True


# ============ Unit Schemas ============

class UnitBase(BaseModel):
    """Base schema for Unit"""
    unit_name: str = Field(..., description="Unit name (e.g., 'Fmn A')")
    file_path: Optional[str] = Field(None, description="Original file path")


class UnitCreate(UnitBase):
    """Schema for creating a new unit"""
    dataset_id: int


class UnitResponse(UnitBase):
    """Schema for unit response"""
    id: int
    dataset_id: int
    
    class Config:
        from_attributes = True


# ============ SheetData Schemas ============

class SheetDataBase(BaseModel):
    """Base schema for SheetData"""
    sheet_type: str = Field(..., description="Type of sheet (e.g., 'APPX_A_BVEH')")
    row_data: List[Dict[str, Any]] = Field(..., description="Array of row data objects")


class SheetDataCreate(SheetDataBase):
    """Schema for creating sheet data"""
    unit_id: int


class SheetDataResponse(SheetDataBase):
    """Schema for sheet data response"""
    id: int
    unit_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Upload Schemas ============

class UploadRequest(BaseModel):
    """Schema for upload request"""
    directory_path: str = Field(..., description="Path to directory containing unit data")
    tag: Optional[str] = Field(None, description="Custom tag for dataset (auto-generated if not provided)")
    description: Optional[str] = Field(None, description="Optional description")


class UploadResponse(BaseModel):
    """Schema for upload response"""
    success: bool
    message: str
    dataset: Optional[DatasetResponse] = None
    units_processed: int = 0
    errors: List[str] = Field(default_factory=list)


# ============ Data Query Schemas ============

class DataQueryParams(BaseModel):
    """Schema for querying data"""
    tag: str = Field(..., description="Dataset tag")
    unit_filter: str = Field(default="All", description="Unit filter ('All' or specific unit name)")
    sheet_type: Optional[str] = Field(None, description="Filter by specific sheet type")


class DataResponse(BaseModel):
    """Schema for data response"""
    tag: str
    unit_filter: str
    sheets: Dict[str, List[Dict[str, Any]]] = Field(..., description="Data organized by sheet type")


# ============ Comparison Schemas ============

class ComparisonRequest(BaseModel):
    """Schema for comparison request"""
    tag1: str = Field(..., description="First dataset tag")
    tag2: str = Field(..., description="Second dataset tag")
    sheet_type: str = Field(..., description="Sheet type to compare")
    prompt_template: str = Field(..., description="Custom prompt template for LLM comparison")


class ComparisonResponse(BaseModel):
    """Schema for comparison response"""
    tag1: str
    tag2: str
    sheet_type: str
    comparison_text: str = Field(..., description="LLM-generated comparison text")
    readiness_data: List[Dict] = Field(default_factory=list, description="Per-unit readiness data for chart")
    generated_at: datetime = Field(default_factory=datetime.now)


# ============ Summary Schemas ============

class SummaryRequest(BaseModel):
    """Schema for data summary generation request"""
    tag: str = Field(..., description="Dataset tag")
    unit_filter: str = Field(default="All", description="Unit filter ('All' or specific unit name)")
    sheet_type: str = Field(..., description="Sheet type to summarize")
    prompt_template: str = Field(..., description="Custom prompt template for LLM")


class SummaryResponse(BaseModel):
    """Schema for summary response"""
    tag: str
    sheet_type: str
    unit_filter: str
    summary_text: str = Field(..., description="LLM-generated summary")
    generated_at: datetime = Field(default_factory=datetime.now)


# ============ Utility Schemas ============

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    success: bool = False
