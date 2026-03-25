"""
Data router for FRS Data Management System API.
Handles all data-related endpoints.
"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Dataset, Unit, SheetData, LocalWorkshop, RemoteWorkshop
from schemas import (
    DatasetResponse, UploadRequest, UploadResponse, DataResponse,
    ComparisonRequest, ComparisonResponse, MessageResponse, ErrorResponse,
    UnitResponse, SummaryRequest, SummaryResponse
)
from services.upload_service import process_directory
# DEMO: Import demo service for hardcoded data loading
from services.demo_service import load_demo_data, clean_all_data, DEMO_BASE_PATH, DEMO_FORMATION
from services.llm_service import compare_datasets as llm_compare_datasets, generate_summary
from config import SHEET_TYPE_ORDER
from processors import aggregate_by_category

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/config")
async def get_config():
    """
    Get application configuration including demo data paths.
    """
    return {
        "demo_base_path": DEMO_BASE_PATH,
        "demo_formation": DEMO_FORMATION
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_directory(
    request: UploadRequest,
    db: Session = Depends(get_db)
):
    """
    Upload and process a directory containing FRS data.
    
    Args:
        request: Upload request with directory path and optional tag
        db: Database session
    
    Returns:
        Upload response with dataset information and any errors
    """
    try:
        success, message, dataset, errors = process_directory(
            directory_path=request.directory_path,
            tag=request.tag,
            description=request.description,
            db=db
        )
        
        if success and dataset:
            # Count units
            unit_count = db.query(Unit).filter(Unit.dataset_id == dataset.id).count()
            
            dataset_response = DatasetResponse(
                id=dataset.id,
                tag=dataset.tag,
                upload_date=dataset.upload_date,
                month_label=dataset.month_label,
                description=dataset.description,
                unit_count=unit_count
            )
            
            return UploadResponse(
                success=True,
                message=message,
                dataset=dataset_response,
                units_processed=unit_count,
                errors=errors
            )
        else:
            return UploadResponse(
                success=False,
                message=message,
                units_processed=0,
                errors=errors
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DEMO: New endpoints for simplified demo version
@router.post("/demo/load", response_model=MessageResponse)
async def load_demo_data_endpoint(db: Session = Depends(get_db)):
    """
    Load demo data from hardcoded path.
    Loads Fmn D data from Nov and Dec directories.
    
    Args:
        db: Database session
    
    Returns:
        Success message with any errors encountered
    """
    try:
        success, message, errors = load_demo_data(db)
        
        if success:
            return MessageResponse(message=message)
        else:
            # Return error as 400 with details
            error_detail = f"{message}. Errors: {'; '.join(errors)}" if errors else message
            raise HTTPException(status_code=400, detail=error_detail)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demo/clean", response_model=MessageResponse)
async def clean_demo_data_endpoint(db: Session = Depends(get_db)):
    """
    Clean all data from the database.
    
    Args:
        db: Database session
    
    Returns:
        Success message
    """
    try:
        success, message = clean_all_data(db)
        
        if success:
            return MessageResponse(message=message)
        else:
            raise HTTPException(status_code=400, detail=message)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(db: Session = Depends(get_db)):
    """
    Get list of all uploaded datasets.
    
    Args:
        db: Database session
    
    Returns:
        List of datasets with metadata
    """
    try:
        datasets = db.query(Dataset).order_by(Dataset.upload_date.desc()).all()
        
        result = []
        for dataset in datasets:
            # Calculate unit_count based on dataset type
            if "Local Workshop" in dataset.tag:
                # For Local Workshop, count distinct formations (all are Formation D)
                # Use raw SQL via text() to query JSON field
                from sqlalchemy import text
                query_result = db.execute(
                    text("SELECT COUNT(DISTINCT row_data->>'Formation') FROM local_workshop WHERE dataset_id = :dataset_id"),
                    {"dataset_id": dataset.id}
                )
                unit_count = query_result.scalar() or 0
            elif "Remote Workshop" in dataset.tag:
                # For Remote Workshop, count distinct formations (all are Formation D)
                from sqlalchemy import text
                query_result = db.execute(
                    text("SELECT COUNT(DISTINCT row_data->>'Formation') FROM remote_workshop WHERE dataset_id = :dataset_id"),
                    {"dataset_id": dataset.id}
                )
                unit_count = query_result.scalar() or 0
            else:
                # For Formation datasets, count units in unit table
                unit_count = db.query(Unit).filter(Unit.dataset_id == dataset.id).count()
            
            result.append(DatasetResponse(
                id=dataset.id,
                tag=dataset.tag,
                upload_date=dataset.upload_date,
                month_label=dataset.month_label,
                description=dataset.description,
                unit_count=unit_count
            ))
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/{tag}", response_model=DataResponse)
async def get_data(
    tag: str,
    unit_filter: str = Query(default="All", description="Filter by unit name or 'All'"),
    sheet_type: Optional[str] = Query(default=None, description="Filter by specific sheet type"),
    db: Session = Depends(get_db)
):
    """
    Get data for a specific dataset with optional filtering.
    Supports three types of datasets:
    1. Formation datasets (November/December 2025) - A Veh, B Veh, C Veh, ARMT, SA
    2. Local Workshop datasets - FR sheet
    3. Remote Workshop datasets - Eng, EOA Spares, MUA sheets
    
    Args:
        tag: Dataset tag
        unit_filter: Unit name filter ("All" or specific unit like "Fmn A")
        sheet_type: Optional sheet type filter
        db: Database session
    
    Returns:
        Data organized by sheet type
    """
    try:
        # Find dataset
        dataset = db.query(Dataset).filter(Dataset.tag == tag).first()
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {tag}")
        
        # Determine dataset type based on tag
        is_local_workshop = "Local Workshop" in tag
        is_remote_workshop = "Remote Workshop" in tag
        
        sheets = {}
        
        if is_local_workshop:
            # Query LocalWorkshop table
            query = db.query(LocalWorkshop).filter(LocalWorkshop.dataset_id == dataset.id)
            
            # Apply sheet type filter
            if sheet_type:
                query = query.filter(LocalWorkshop.sheet_name == sheet_type)
            
            workshop_records = query.all()
            
            # Organize data by sheet name
            sheets_temp = {}
            for record in workshop_records:
                if record.sheet_name not in sheets_temp:
                    sheets_temp[record.sheet_name] = []
                sheets_temp[record.sheet_name].append(record.row_data)
            
            # Apply unit filter if specified (Local Workshop uses 'Unit' not 'Units')
            if unit_filter and unit_filter not in ["All", "All Units (Aggregated)"]:
                for sheet_name, data in sheets_temp.items():
                    filtered_data = [row for row in data if row.get('Unit') == unit_filter]
                    if filtered_data:
                        sheets[sheet_name] = filtered_data
            else:
                sheets = sheets_temp
        
        elif is_remote_workshop:
            # Query RemoteWorkshop table
            query = db.query(RemoteWorkshop).filter(RemoteWorkshop.dataset_id == dataset.id)
            
            # Apply sheet type filter
            if sheet_type:
                query = query.filter(RemoteWorkshop.sheet_name == sheet_type)
            
            workshop_records = query.all()
            
            # Organize data by sheet name
            sheets_temp = {}
            for record in workshop_records:
                if record.sheet_name not in sheets_temp:
                    sheets_temp[record.sheet_name] = []
                sheets_temp[record.sheet_name].append(record.row_data)
            
            # Order sheets: Eng, EOA Spares, VOR Spares
            for sheet_name in ["Eng", "EOA Spares", "VOR Spares"]:
                if sheet_name in sheets_temp:
                    sheets[sheet_name] = sheets_temp[sheet_name]
        
        else:
            # Standard formation dataset - query Unit/SheetData tables
            query = db.query(SheetData).join(Unit).filter(Unit.dataset_id == dataset.id)
            
            # Apply unit filter
            if unit_filter != "All":
                query = query.filter(Unit.unit_name == unit_filter)
            
            # Apply sheet type filter
            if sheet_type:
                query = query.filter(SheetData.sheet_type == sheet_type)
            
            # Fetch data
            sheet_data_records = query.all()
            
            # Organize data by sheet type in standard order
            # First, collect all data by sheet type
            sheets_temp = {}
            for record in sheet_data_records:
                if record.sheet_type not in sheets_temp:
                    sheets_temp[record.sheet_type] = []
                sheets_temp[record.sheet_type].extend(record.row_data)
            
            # Apply aggregation if "All" units selected
            # DEMO: For demo purposes, disable aggregation to show raw data
            # if unit_filter == "All":
            #     # Aggregate by category for each sheet type
            #     for sheet_type, rows in sheets_temp.items():
            #         sheets_temp[sheet_type] = aggregate_by_category(rows, use_ai_for_remarks=False)
            # else:
            if True:  # Always show non-aggregated data
                # Even for single units, standardize column names for consistency
                from processors.data_cleaner import standardize_column_name
                for sheet_type, rows in sheets_temp.items():
                    standardized_rows = []
                    for row in rows:
                        standardized_row = {}
                        for key, value in row.items():
                            standard_key = standardize_column_name(key)
                            standardized_row[standard_key] = value
                        standardized_rows.append(standardized_row)
                    
                    # For ARMT sheets, rename 'Category (Make & Type)' to 'Make & Eqpt' and reorder
                    if standardized_rows:
                        # Check for ARMT-specific columns
                        armt_indicators = ['Eng/ Brl', 'Spares', 'MR', 'FR', 'OBE', 'PMC (Nos) (Due to OH)', 'NMC%', 'PMC%', 'Avl%']
                        sample_keys = list(standardized_rows[0].keys())
                        is_armt = any(col in sample_keys for col in armt_indicators)
                        
                        if is_armt and 'Category (Make & Type)' in sample_keys:
                            # Rename category column for ARMT sheets and maintain proper order
                            reordered_rows = []
                            for row in standardized_rows:
                                new_row = {}
                                for key in row.keys():
                                    if key == 'Category (Make & Type)':
                                        new_row['Make & Eqpt'] = row[key]
                                    else:
                                        new_row[key] = row[key]
                                reordered_rows.append(new_row)
                            standardized_rows = reordered_rows
                    
                    sheets_temp[sheet_type] = standardized_rows
            
            # Build ordered dictionary following SHEET_TYPE_ORDER
            for sheet_type in SHEET_TYPE_ORDER:
                if sheet_type in sheets_temp:
                    sheets[sheet_type] = sheets_temp[sheet_type]
            
            # Add any additional sheets not in standard order
            for sheet_type, data in sheets_temp.items():
                if sheet_type not in sheets:
                    sheets[sheet_type] = data
        return DataResponse(
            tag=tag,
            unit_filter=unit_filter,
            sheets=sheets
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/{tag}/units", response_model=List[str])
async def get_units(
    tag: str,
    db: Session = Depends(get_db)
):
    """
    Get list of units in a dataset.
    
    Args:
        tag: Dataset tag
        db: Database session
    
    Returns:
        List of unit names
    """
    try:
        # Find dataset
        dataset = db.query(Dataset).filter(Dataset.tag == tag).first()
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {tag}")
        
        # Get all units
        units = db.query(Unit.unit_name).filter(Unit.dataset_id == dataset.id).distinct().all()
        
        return [unit[0] for unit in units]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=ComparisonResponse)
async def compare_datasets(
    request: ComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    Compare two datasets for a specific sheet type and generate LLM-powered analysis.
    
    Args:
        request: Comparison request with two dataset tags, sheet type, and custom prompt
        db: Database session
    
    Returns:
        LLM-generated comparison text
    """
    try:
        # Perform comparison
        result = llm_compare_datasets(
            tag1=request.tag1,
            tag2=request.tag2,
            sheet_type=request.sheet_type,
            prompt_template=request.prompt_template,
            db=db
        )
        
        return ComparisonResponse(
            tag1=request.tag1,
            tag2=request.tag2,
            sheet_type=request.sheet_type,
            comparison_text=result["comparison_text"],
            readiness_data=result["readiness_data"],
            generated_at=datetime.now()
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/datasets/{tag}", response_model=MessageResponse)
async def delete_dataset(
    tag: str,
    db: Session = Depends(get_db)
):
    """
    Delete a dataset and all associated data.
    
    Args:
        tag: Dataset tag to delete
        db: Database session
    
    Returns:
        Success message
    """
    try:
        # Find dataset
        dataset = db.query(Dataset).filter(Dataset.tag == tag).first()
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {tag}")
        
        # Count units before deletion
        unit_count = db.query(Unit).filter(Unit.dataset_id == dataset.id).count()
        
        # Delete dataset (cascade will delete units and sheet_data)
        db.delete(dataset)
        db.commit()
        
        return MessageResponse(
            message=f"Successfully deleted dataset '{tag}' with {unit_count} units",
            success=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-summary", response_model=SummaryResponse)
async def create_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db)
):
    """
    Generate executive summary for selected data using LLM.
    
    Args:
        request: Summary request with dataset tag, filters, and prompt template
        db: Database session
    
    Returns:
        Summary response with LLM-generated analysis
    """
    try:
        summary_text = generate_summary(
            tag=request.tag,
            unit_filter=request.unit_filter,
            sheet_type=request.sheet_type,
            prompt_template=request.prompt_template,
            db=db
        )
        
        return SummaryResponse(
            tag=request.tag,
            sheet_type=request.sheet_type,
            unit_filter=request.unit_filter,
            summary_text=summary_text
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=MessageResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Success message
    """
    return MessageResponse(message="Service is healthy", success=True)
