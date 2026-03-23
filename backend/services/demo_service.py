"""
Demo service for hardcoded data loading.
Loads FRS data from a predefined directory structure for demo purposes.
"""
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import pandas as pd

from models import Dataset, Unit, SheetData, LocalWorkshop, RemoteWorkshop
from parsers.excel_parser import parse_sheet_with_detection
from processors.data_cleaner import clean_dataframe, dataframe_to_json, calculate_derived_fields

# Hardcoded base path for demo
DEMO_BASE_PATH = r"C:\Anu\APT\apt\army\fortwilliam\code\fwDemo\data\FRS_cleaned"

# Formation to process (only Fmn D has complete data)
DEMO_FORMATION = "Fmn D"

# Sheet mappings for different file types
FORMATION_SHEETS = ["A Vehicle", "B Vehicle", "C Vehicle", "ARMT", "SA"]
LOCAL_WORKSHOP_SHEET = "FR"
REMOTE_WORKSHOP_SHEETS = ["Eng", "EOA Spares", "MUA"]

# Map Excel sheet names to database sheet type keys
SHEET_TYPE_MAPPING = {
    "A Vehicle": "APPX_A_AVEH",
    "B Vehicle": "APPX_A_BVEH",
    "C Vehicle": "APPX_A_CVEH",
    "ARMT": "ARMT",
    "SA": "SA"
}


def get_file_by_pattern(directory: Path, pattern: str) -> Optional[Path]:
    """
    Find a file in directory that matches the pattern.
    
    Args:
        directory: Directory to search
        pattern: Partial string to match in filename
    
    Returns:
        Path to matching file or None
    """
    if not directory.exists():
        return None
    
    for file_path in directory.iterdir():
        if file_path.is_file() and pattern.lower() in file_path.name.lower():
            if file_path.suffix.lower() in ['.xls', '.xlsx']:
                if not file_path.name.startswith('~$'):  # Skip temp files
                    return file_path
    
    return None


def parse_workshop_sheet(file_path: Path, sheet_name: str) -> pd.DataFrame:
    """
    Parse a workshop sheet with simple header at line 1.
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name to parse
    
    Returns:
        DataFrame with parsed data
    """
    try:
        # Determine engine based on file extension
        engine = 'openpyxl' if file_path.suffix == '.xlsx' else 'xlrd'
        
        # Read with first row as header
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=0, engine=engine)
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    except Exception as e:
        raise Exception(f"Failed to parse sheet '{sheet_name}' from {file_path.name}: {str(e)}")


def process_formation_file(file_path: Path, unit_name: str, dataset_id: int, db: Session) -> Tuple[bool, str, List[str]]:
    """
    Process formation file (2025-D pattern) - parse A Vehicle, B Vehicle, C Vehicle, ARMT, SA sheets.
    
    Args:
        file_path: Path to formation Excel file
        unit_name: Name of the unit (e.g., "Fmn D Nov")
        dataset_id: Dataset ID to associate data with
        db: Database session
    
    Returns:
        Tuple of (success, message, errors)
    """
    errors = []
    sheets_processed = 0
    
    try:
        # Create unit entry
        unit = Unit(
            dataset_id=dataset_id,
            unit_name=unit_name,
            file_path=str(file_path)
        )
        db.add(unit)
        db.flush()  # Get unit.id
        
        # Process each formation sheet
        for sheet_type in FORMATION_SHEETS:
            try:
                # Parse sheet with existing parser
                df = parse_sheet_with_detection(file_path, sheet_type)
                
                # Clean data
                df = clean_dataframe(df)
                
                # Calculate derived fields
                df = calculate_derived_fields(df, sheet_type)
                
                # Convert to JSON
                json_data = dataframe_to_json(df)
                
                # Map sheet name to proper sheet type key
                sheet_type_key = SHEET_TYPE_MAPPING.get(sheet_type, sheet_type.upper().replace(" ", "_"))
                
                # Store in database
                sheet_data = SheetData(
                    unit_id=unit.id,
                    sheet_type=sheet_type_key,
                    row_data=json_data
                )
                db.add(sheet_data)
                sheets_processed += 1
                
            except Exception as e:
                error_msg = f"Failed to process sheet '{sheet_type}' in {file_path.name}: {str(e)}"
                errors.append(error_msg)
                print(f"[demo_service] {error_msg}")
        
        # Don't commit here - let the caller handle it
        # db.commit()
        
        if sheets_processed > 0:
            return True, f"Processed {sheets_processed} sheets from {file_path.name}", errors
        else:
            return False, f"No sheets successfully processed from {file_path.name}", errors
            
    except Exception as e:
        # Don't rollback here - let the caller handle it
        # db.rollback()
        error_msg = f"Failed to process formation file {file_path.name}: {str(e)}"
        errors.append(error_msg)
        return False, error_msg, errors


def process_local_workshop(file_path: Path, dataset_id: int, db: Session) -> Tuple[bool, str, List[str]]:
    """
    Process Local Workshop file - parse FR sheet.
    
    Args:
        file_path: Path to Local Workshop Excel file
        dataset_id: Dataset ID to associate data with
        db: Database session
    
    Returns:
        Tuple of (success, message, errors)
    """
    errors = []
    rows_processed = 0
    
    try:
        # Parse FR sheet
        df = parse_workshop_sheet(file_path, LOCAL_WORKSHOP_SHEET)
        
        # Check if required columns exist (Local Workshop uses 'Units' not 'Unit')
        if 'Units' not in df.columns or 'Category' not in df.columns:
            error_msg = f"Required columns 'Units' and 'Category' not found in FR sheet of {file_path.name}"
            errors.append(error_msg)
            return False, error_msg, errors
        
        # Process each row
        for idx, row in df.iterrows():
            unit = str(row.get('Units', '')).strip()  # Note: 'Units' not 'Unit'
            category = str(row.get('Category', '')).strip()
            
            # Skip empty rows
            if not unit or not category or unit == 'nan' or category == 'nan':
                continue
            
            # Convert row to dict
            row_dict = row.to_dict()
            # Convert any NaN values to None and datetime objects to strings for JSON serialization
            row_dict = {
                k: (None if pd.isna(v) else (v.isoformat() if isinstance(v, (pd.Timestamp, datetime)) else v))
                for k, v in row_dict.items()
            }
            
            # Create LocalWorkshop entry
            local_workshop = LocalWorkshop(
                dataset_id=dataset_id,
                unit=unit,
                category=category,
                row_data=row_dict
            )
            db.add(local_workshop)
            rows_processed += 1
        
        # Don't commit here - let the caller handle it
        # db.commit()
        
        if rows_processed > 0:
            return True, f"Processed {rows_processed} rows from Local Workshop FR sheet", errors
        else:
            return False, "No valid rows found in Local Workshop FR sheet", errors
            
    except Exception as e:
        # Don't rollback here - let the caller handle it
        # db.rollback()
        error_msg = f"Failed to process Local Workshop file {file_path.name}: {str(e)}"
        errors.append(error_msg)
        return False, error_msg, errors


def process_remote_workshop(file_path: Path, dataset_id: int, db: Session) -> Tuple[bool, str, List[str]]:
    """
    Process Remote Workshop file - parse Eng, EOA Spares, MUA sheets.
    
    Args:
        file_path: Path to Remote Workshop Excel file
        dataset_id: Dataset ID to associate data with
        db: Database session
    
    Returns:
        Tuple of (success, message, errors)
    """
    errors = []
    total_rows_processed = 0
    
    try:
        # Process each remote workshop sheet
        for sheet_name in REMOTE_WORKSHOP_SHEETS:
            try:
                df = parse_workshop_sheet(file_path, sheet_name)
                
                # Check if required columns exist (Remote Workshop uses 'Units' not 'Unit')
                if 'Units' not in df.columns or 'Category' not in df.columns:
                    error_msg = f"Required columns 'Units' and 'Category' not found in {sheet_name} sheet"
                    errors.append(error_msg)
                    continue
                
                rows_processed = 0
                
                # Process each row
                for idx, row in df.iterrows():
                    unit = str(row.get('Units', '')).strip()  # Note: 'Units' not 'Unit'
                    category = str(row.get('Category', '')).strip()
                    
                    # Skip empty rows
                    if not unit or not category or unit == 'nan' or category == 'nan':
                        continue
                    
                    # Convert row to dict
                    row_dict = row.to_dict()
                    # Convert any NaN values to None and datetime objects to strings for JSON serialization
                    row_dict = {
                        k: (None if pd.isna(v) else (v.isoformat() if isinstance(v, (pd.Timestamp, datetime)) else v))
                        for k, v in row_dict.items()
                    }
                    
                    # Create RemoteWorkshop entry
                    remote_workshop = RemoteWorkshop(
                        dataset_id=dataset_id,
                        sheet_name=sheet_name,
                        unit=unit,
                        category=category,
                        row_data=row_dict
                    )
                    db.add(remote_workshop)
                    rows_processed += 1
                
                total_rows_processed += rows_processed
                print(f"[demo_service] Processed {rows_processed} rows from {sheet_name} sheet")
                
            except Exception as e:
                error_msg = f"Failed to process sheet '{sheet_name}' in {file_path.name}: {str(e)}"
                errors.append(error_msg)
                print(f"[demo_service] {error_msg}")
        
        # Don't commit here - let the caller handle it
        # db.commit()
        
        if total_rows_processed > 0:
            return True, f"Processed {total_rows_processed} total rows from Remote Workshop", errors
        else:
            return False, "No valid rows found in Remote Workshop sheets", errors
            
    except Exception as e:
        # Don't rollback here - let the caller handle it
        # db.rollback()
        error_msg = f"Failed to process Remote Workshop file {file_path.name}: {str(e)}"
        errors.append(error_msg)
        return False, error_msg, errors


def load_demo_data(db: Session) -> Tuple[bool, str, List[str]]:
    """
    Load all demo data from hardcoded path.
    Processes Nov and Dec data for Fmn D only.
    Creates separate datasets for Formation data, Local Workshop, and Remote Workshop.
    
    Args:
        db: Database session
    
    Returns:
        Tuple of (success, message, errors)
    """
    base_path = Path(DEMO_BASE_PATH)
    all_errors = []
    
    if not base_path.exists():
        error_msg = f"Demo data path does not exist: {DEMO_BASE_PATH}"
        return False, error_msg, [error_msg]
    
    # Process both Nov and Dec directories
    months = ["Nov", "Dec"]
    month_full_names = {"Nov": "November", "Dec": "December"}
    datasets_created = 0
    
    for month in months:
        month_full = month_full_names[month]
        month_dir = base_path / month
        
        if not month_dir.exists():
            error_msg = f"Month directory not found: {month_dir}"
            all_errors.append(error_msg)
            continue
        
        # Find Fmn D directory
        fmn_d_dir = None
        for subdir in month_dir.iterdir():
            if subdir.is_dir() and DEMO_FORMATION in subdir.name:
                fmn_d_dir = subdir
                break
        
        if not fmn_d_dir:
            error_msg = f"Formation D directory not found in {month_dir}"
            all_errors.append(error_msg)
            continue
        
        print(f"[demo_service] Processing {fmn_d_dir.name}...")
        
        # Create three separate datasets for each month
        # 1. Formation Data Dataset
        formation_tag = f"{month_full} 2025"
        existing = db.query(Dataset).filter(Dataset.tag == formation_tag).first()
        if existing:
            error_msg = f"Dataset '{formation_tag}' already exists. Please clean the database first."
            all_errors.append(error_msg)
            continue
        
        formation_dataset = Dataset(
            tag=formation_tag,
            month_label=month_full,
            description=f"Formation D data - {month_full} 2025"
        )
        db.add(formation_dataset)
        db.flush()
        
        # Process formation file
        formation_file = get_file_by_pattern(fmn_d_dir, "2025-D")
        if formation_file:
            success, msg, errors = process_formation_file(
                formation_file, 
                fmn_d_dir.name, 
                formation_dataset.id, 
                db
            )
            all_errors.extend(errors)
            print(f"[demo_service] Formation file: {msg}")
        else:
            error_msg = f"Formation file (2025-D pattern) not found in {fmn_d_dir.name}"
            all_errors.append(error_msg)
        
        datasets_created += 1
        
        # 2. Local Workshop Dataset
        local_tag = f"Local Workshop {month_full} 2025"
        existing_local = db.query(Dataset).filter(Dataset.tag == local_tag).first()
        if not existing_local:
            local_dataset = Dataset(
                tag=local_tag,
                month_label=month_full,
                description=f"Local Workshop data for Formation D - {month_full} 2025"
            )
            db.add(local_dataset)
            db.flush()
            
            local_file = get_file_by_pattern(fmn_d_dir, "Local")
            if local_file:
                success, msg, errors = process_local_workshop(local_file, local_dataset.id, db)
                all_errors.extend(errors)
                print(f"[demo_service] Local Workshop: {msg}")
            else:
                error_msg = f"Local Workshop file not found in {fmn_d_dir.name}"
                all_errors.append(error_msg)
            
            datasets_created += 1
        
        # 3. Remote Workshop Dataset
        remote_tag = f"Remote Workshop {month_full} 2025"
        existing_remote = db.query(Dataset).filter(Dataset.tag == remote_tag).first()
        if not existing_remote:
            remote_dataset = Dataset(
                tag=remote_tag,
                month_label=month_full,
                description=f"Remote Workshop data for Formation D - {month_full} 2025"
            )
            db.add(remote_dataset)
            db.flush()
            
            remote_file = get_file_by_pattern(fmn_d_dir, "Remote")
            if remote_file:
                success, msg, errors = process_remote_workshop(remote_file, remote_dataset.id, db)
                all_errors.extend(errors)
                print(f"[demo_service] Remote Workshop: {msg}")
            else:
                error_msg = f"Remote Workshop file not found in {fmn_d_dir.name}"
                all_errors.append(error_msg)
            
            datasets_created += 1
    
    if datasets_created > 0:
        db.commit()
        return True, f"Successfully loaded {datasets_created} datasets", all_errors
    else:
        db.rollback()
        return False, "Failed to load any datasets", all_errors


def clean_all_data(db: Session) -> Tuple[bool, str]:
    """
    Clean all data from the database.
    
    Args:
        db: Database session
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # Delete all datasets (cascade will delete related data)
        deleted_count = db.query(Dataset).delete()
        db.commit()
        
        return True, f"Successfully deleted {deleted_count} datasets and all related data"
    except Exception as e:
        db.rollback()
        error_msg = f"Failed to clean database: {str(e)}"
        return False, error_msg
