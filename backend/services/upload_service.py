"""
Upload service for FRS Data Management System.
Handles directory processing, file parsing, and database storage.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models import Dataset, Unit, SheetData
from parsers.dictionary_parser import parse_dictionary
from parsers.excel_parser import parse_excel_file
from processors.data_cleaner import clean_dataframe, dataframe_to_json, calculate_derived_fields


def detect_month_from_path(directory_path: str) -> Optional[str]:
    """
    Auto-detect month from directory path or name.
    
    Args:
        directory_path: Path to directory
    
    Returns:
        Month name (e.g., "November", "December") or None
    """
    path_str = str(directory_path).lower()
    
    month_mappings = {
        'jan': 'January',
        'feb': 'February',
        'mar': 'March',
        'apr': 'April',
        'may': 'May',
        'jun': 'June',
        'jul': 'July',
        'aug': 'August',
        'sep': 'September',
        'oct': 'October',
        'nov': 'November',
        'dec': 'December'
    }
    
    for abbr, full_name in month_mappings.items():
        if abbr in path_str or full_name.lower() in path_str:
            return full_name
    
    return None


def extract_unit_name(directory_name: str) -> Optional[str]:
    """
    Extract unit name from directory name.
    
    Args:
        directory_name: Name of unit directory (e.g., "Fmn A Nov", "Fmn B Dec")
    
    Returns:
        Unit name (e.g., "Fmn A", "Fmn B") or None
    """
    # Pattern to match "Fmn X" where X is a letter
    match = re.search(r'Fmn\s+([A-K])', directory_name, re.IGNORECASE)
    if match:
        letter = match.group(1).upper()
        return f"Fmn {letter}"
    
    return None


def find_excel_files(directory: Path) -> List[Path]:
    """
    Find all Excel files in a directory (non-recursive).
    
    Args:
        directory: Directory path
    
    Returns:
        List of Excel file paths
    """
    excel_files = []
    
    if not directory.exists() or not directory.is_dir():
        return excel_files
    
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.xls', '.xlsx']:
            # Skip temporary Excel files
            if not file_path.name.startswith('~$'):
                excel_files.append(file_path)
    
    return excel_files


def process_directory(directory_path: str, tag: Optional[str], description: Optional[str],
                     db: Session) -> Tuple[bool, str, Optional[Dataset], List[str]]:
    """
    Process a directory containing FRS data from multiple units.
    
    Args:
        directory_path: Path to directory containing unit subdirectories
        tag: Custom tag for dataset (auto-generated if None)
        description: Optional description
        db: Database session
    
    Returns:
        Tuple of (success, message, dataset, errors)
    """
    errors = []
    
    try:
        directory = Path(directory_path)
        
        if not directory.exists():
            return False, f"Directory not found: {directory_path}", None, ["Directory does not exist"]
        
        if not directory.is_dir():
            return False, f"Path is not a directory: {directory_path}", None, ["Not a directory"]
        
        # Detect month from path
        month_label = detect_month_from_path(directory_path)
        
        # Generate tag if not provided
        if not tag:
            month_str = month_label if month_label else "Unknown"
            year_str = datetime.now().year
            tag = f"FRS {month_str} {year_str}"
        
        # Check if tag already exists
        existing_dataset = db.query(Dataset).filter(Dataset.tag == tag).first()
        if existing_dataset:
            return False, f"Dataset with tag '{tag}' already exists", None, ["Duplicate tag"]
        
        # Get column metadata (this always succeeds with fallback to defaults)
        dictionary_mapping = parse_dictionary()
        
        # Create dataset record
        dataset = Dataset(
            tag=tag,
            month_label=month_label,
            description=description
        )
        db.add(dataset)
        db.flush()  # Get dataset ID without committing
        
        # Find unit subdirectories
        unit_dirs = [d for d in directory.iterdir() if d.is_dir()]
        
        if not unit_dirs:
            errors.append("No unit subdirectories found")
            return False, "No unit subdirectories found", None, errors
        
        units_processed = 0
        
        # Process each unit directory
        for unit_dir in unit_dirs:
            try:
                # Extract unit name
                unit_name = extract_unit_name(unit_dir.name)
                if not unit_name:
                    errors.append(f"Could not extract unit name from: {unit_dir.name}")
                    continue
                
                # Find Excel files in unit directory
                excel_files = find_excel_files(unit_dir)
                
                if not excel_files:
                    errors.append(f"No Excel files found in: {unit_dir.name}")
                    continue
                
                # Process first Excel file (typically there's only one per unit)
                excel_file = excel_files[0]
                
                try:
                    # Parse Excel file
                    parsed_sheets = parse_excel_file(str(excel_file), dictionary_mapping)
                    
                    if not parsed_sheets:
                        errors.append(f"No sheets parsed from: {excel_file.name}")
                        continue
                    
                    # Create unit record
                    unit = Unit(
                        dataset_id=dataset.id,
                        unit_name=unit_name,
                        file_path=str(excel_file)
                    )
                    db.add(unit)
                    db.flush()  # Get unit ID
                    
                    # Process each sheet
                    for sheet_type, df in parsed_sheets.items():
                        try:
                            # Calculate derived fields (for sheets like A veh with auto-generated columns)
                            df_with_calcs = calculate_derived_fields(df, sheet_type)
                            
                            # Clean data - use 'zero' fill strategy for A veh to ensure missing values become 0 for numbers, empty for text
                            fill_strategy = 'zero' if sheet_type == 'APPX_A_AVEH' else 'drop'
                            cleaned_df = clean_dataframe(df_with_calcs, fill_strategy=fill_strategy)
                            
                            # Convert to JSON
                            row_data = dataframe_to_json(cleaned_df)
                            
                            # Create sheet data record
                            sheet_data = SheetData(
                                unit_id=unit.id,
                                sheet_type=sheet_type,
                                row_data=row_data
                            )
                            db.add(sheet_data)
                        
                        except Exception as e:
                            errors.append(f"Failed to process sheet {sheet_type} in {excel_file.name}: {str(e)}")
                    
                    units_processed += 1
                
                except Exception as e:
                    errors.append(f"Failed to parse Excel file {excel_file.name}: {str(e)}")
            
            except Exception as e:
                errors.append(f"Failed to process unit directory {unit_dir.name}: {str(e)}")
        
        # Commit transaction
        db.commit()
        db.refresh(dataset)
        
        if units_processed == 0:
            return False, "No units were successfully processed", dataset, errors
        
        success_message = f"Successfully processed {units_processed} unit(s)"
        if errors:
            success_message += f" with {len(errors)} warning(s)"
        
        return True, success_message, dataset, errors
    
    except Exception as e:
        db.rollback()
        return False, f"Upload failed: {str(e)}", None, [str(e)]


# For testing and debugging
if __name__ == "__main__":
    # Test month detection
    test_paths = [
        "data/FRS_Sample/Nov",
        "data/FRS_Sample/Dec",
        "C:\\Users\\Data\\November 2025",
        "/mnt/data/december_data"
    ]
    
    print("Testing month detection:")
    for path in test_paths:
        month = detect_month_from_path(path)
        print(f"  {path} -> {month}")
    
    print("\nTesting unit name extraction:")
    test_dirs = ["Fmn A Nov", "Fmn B Dec", "FMN C NOV", "Formation D"]
    for dir_name in test_dirs:
        unit = extract_unit_name(dir_name)
        print(f"  {dir_name} -> {unit}")
