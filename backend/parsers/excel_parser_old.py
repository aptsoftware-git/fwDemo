"""
Excel parser for FRS Data Management System.
Parses Excel files (.xls and .xlsx) with fuzzy sheet name matching.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from difflib import SequenceMatcher
import jellyfish
import openpyxl
import xlrd

from config import SHEET_TYPES, SHEET_TYPE_ORDER
from parsers.dictionary_parser import get_column_mapping


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity between two strings using multiple methods.
    
    Args:
        str1: First string
        str2: Second string
    
    Returns:
        Similarity score between 0 and 1
    """
    # Normalize strings (lowercase, remove extra spaces and special chars)
    s1 = ''.join(c.lower() for c in str1 if c.isalnum() or c.isspace()).strip()
    s2 = ''.join(c.lower() for c in str2 if c.isalnum() or c.isspace()).strip()
    
    # Method 1: Sequence matcher (character-level similarity)
    seq_similarity = SequenceMatcher(None, s1, s2).ratio()
    
    # Method 2: Soundex (phonetic similarity)
    soundex_match = 1.0 if jellyfish.soundex(s1) == jellyfish.soundex(s2) else 0.0
    
    # Combine both methods (weighted average)
    return (seq_similarity * 0.7) + (soundex_match * 0.3)


def match_sheet_name(actual_name: str, expected_names: Dict[str, str], threshold: float = 0.6) -> Optional[str]:
    """
    Match an actual sheet name to expected sheet types using fuzzy matching.
    
    Args:
        actual_name: Actual sheet name from Excel file
        expected_names: Dictionary of sheet_type -> expected_name
        threshold: Minimum similarity threshold (0-1)
    
    Returns:
        Best matching sheet_type or None if no good match found
    """
    best_match = None
    best_score = threshold
    
    for sheet_type, expected_name in expected_names.items():
        similarity = calculate_similarity(actual_name, expected_name)
        if similarity > best_score:
            best_score = similarity
            best_match = sheet_type
    
    return best_match


def parse_excel_file(file_path: str, dictionary_mapping: Dict[str, List[str]] = None) -> Dict[str, pd.DataFrame]:
    """
    Parse an Excel file and extract data from all sheets with fuzzy name matching.
    
    Args:
        file_path: Path to Excel file (.xls or .xlsx)
        dictionary_mapping: Column mapping from dictionary parser (optional)
    
    Returns:
        Dictionary mapping sheet_type to pandas DataFrame
        Example: {'APPX_A_BVEH': df1, 'APPX_A_CVEH': df2, ...}
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is unsupported
        Exception: If parsing fails
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    
    file_ext = file_path.suffix.lower()
    
    if file_ext not in ['.xls', '.xlsx']:
        raise ValueError(f"Unsupported file format: {file_ext}. Expected .xls or .xlsx")
    
    try:
        # Read all sheets from Excel file
        if file_ext == '.xlsx':
            # Use openpyxl engine for .xlsx files
            excel_file = pd.ExcelFile(file_path, engine='openpyxl')
        else:
            # Use xlrd engine for .xls files
            excel_file = pd.ExcelFile(file_path, engine='xlrd')
        
        sheet_names = excel_file.sheet_names
        
        # Dictionary to store parsed sheets
        parsed_sheets = {}
        matched_types = set()
        
        # Try fuzzy matching first
        for sheet_name in sheet_names:
            matched_type = match_sheet_name(sheet_name, SHEET_TYPES)
            
            if matched_type and matched_type not in matched_types:
                # Read the sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Apply column mapping if provided
                if dictionary_mapping and matched_type in dictionary_mapping:
                    column_names = dictionary_mapping[matched_type]
                    # Only rename if we have enough column names
                    if len(column_names) >= len(df.columns):
                        df.columns = column_names[:len(df.columns)]
                
                parsed_sheets[matched_type] = df
                matched_types.add(matched_type)
        
        # Fallback: Use sequence-based matching for unmatched types
        if len(parsed_sheets) < 6:
            # Try to match remaining sheets by sequence
            unmatched_types = [st for st in SHEET_TYPE_ORDER if st not in matched_types]
            unmatched_sheets = [sn for sn in sheet_names if not any(
                match_sheet_name(sn, SHEET_TYPES) == mt for mt in matched_types
            )]
            
            for i, (sheet_type, sheet_name) in enumerate(zip(unmatched_types, unmatched_sheets)):
                if i < len(unmatched_types) and i < len(unmatched_sheets):
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    
                    # Apply column mapping if provided
                    if dictionary_mapping and sheet_type in dictionary_mapping:
                        column_names = dictionary_mapping[sheet_type]
                        if len(column_names) >= len(df.columns):
                            df.columns = column_names[:len(df.columns)]
                    
                    parsed_sheets[sheet_type] = df
        
        excel_file.close()
        
        return parsed_sheets
    
    except Exception as e:
        raise Exception(f"Failed to parse Excel file {file_path}: {str(e)}")


def get_sheet_summary(df: pd.DataFrame) -> Dict:
    """
    Get summary statistics for a DataFrame.
    
    Args:
        df: pandas DataFrame
    
    Returns:
        Dictionary with summary statistics
    """
    return {
        'row_count': len(df),
        'column_count': len(df.columns),
        'columns': list(df.columns),
        'has_null': df.isnull().any().any(),
        'null_counts': df.isnull().sum().to_dict()
    }


def validate_excel_structure(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate that an Excel file has the expected structure.
    
    Args:
        file_path: Path to Excel file
    
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False, ["File does not exist"]
        
        if file_path.suffix.lower() not in ['.xls', '.xlsx']:
            return False, ["Invalid file format (expected .xls or .xlsx)"]
        
        # Try to parse the file
        parsed_sheets = parse_excel_file(str(file_path))
        
        # Check if we have enough sheets
        if len(parsed_sheets) == 0:
            issues.append("No sheets could be parsed")
        elif len(parsed_sheets) < 6:
            issues.append(f"Only {len(parsed_sheets)} out of 6 expected sheets were found")
        
        # Check each sheet for basic validity
        for sheet_type, df in parsed_sheets.items():
            if df.empty:
                issues.append(f"Sheet {sheet_type} is empty")
            elif len(df.columns) == 0:
                issues.append(f"Sheet {sheet_type} has no columns")
        
        is_valid = len(issues) == 0
        
        return is_valid, issues
    
    except Exception as e:
        return False, [f"Validation error: {str(e)}"]


# For testing and debugging
if __name__ == "__main__":
    # Test with sample file
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        # Default test file
        test_file = "../data/FRS_Sample/Nov/Fmn A Nov/Nov 2025.xlsx"
    
    try:
        print(f"Parsing: {test_file}")
        parsed = parse_excel_file(test_file)
        
        print(f"\nSuccessfully parsed {len(parsed)} sheets:")
        for sheet_type, df in parsed.items():
            print(f"\n{sheet_type}:")
            summary = get_sheet_summary(df)
            print(f"  Rows: {summary['row_count']}, Columns: {summary['column_count']}")
            print(f"  Column names: {summary['columns'][:5]}..." if len(summary['columns']) > 5 else f"  Column names: {summary['columns']}")
            print(f"  Has null values: {summary['has_null']}")
    
    except Exception as e:
        print(f"Error: {e}")
