"""
Test script to verify newlines are preserved when reading Excel files
"""
import pandas as pd
import sys
from pathlib import Path

# Test reading an Excel file from the data directory
excel_path = Path("../data/FRS_Sample/Dec/Fmn A Dec")

# Find an Excel file
excel_files = list(excel_path.glob("*.xls*"))
if not excel_files:
    print("No Excel files found!")
    sys.exit(1)

excel_file = excel_files[0]
print(f"Testing file: {excel_file.name}\n")

# Read with openpyxl engine (for .xlsx)
try:
    engine = 'openpyxl' if excel_file.suffix == '.xlsx' else 'xlrd'
    print(f"Using engine: {engine}\n")
    
    # Get sheet names
    xl = pd.ExcelFile(excel_file, engine=engine)
    sheet_names = xl.sheet_names
    print(f"Sheets: {sheet_names}\n")
    
    # Read first sheet that looks like B Veh
    bveh_sheet = None
    for sheet in sheet_names:
        if 'b veh' in sheet.lower() or 'bveh' in sheet.lower():
            bveh_sheet = sheet
            break
    
    if not bveh_sheet:
        bveh_sheet = sheet_names[0]
    
    print(f"Reading sheet: {bveh_sheet}\n")
    
    # Read the sheet
    df = pd.read_excel(excel_file, sheet_name=bveh_sheet, header=None, engine=engine)
    
    # Look for remarks column (usually last column)
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}\n")
    
    # Check last column for newlines
    print("="*80)
    print("Checking last column for newlines")
    print("="*80)
    
    last_col = df.columns[-1]
    for idx, value in df[last_col].items():
        if pd.notna(value) and isinstance(value, str) and len(value) > 20:
            has_newline = '\n' in value
            print(f"\nRow {idx}:")
            print(f"  Length: {len(value)}")
            print(f"  Has \\n: {has_newline}")
            if has_newline:
                print(f"  Newline count: {value.count(chr(10))}")
                print(f"  Content preview:")
                lines = value.split('\n')
                for i, line in enumerate(lines[:5]):  # First 5 lines
                    print(f"    Line {i+1}: {line[:60]}")
                if len(lines) > 5:
                    print(f"    ... ({len(lines)} total lines)")
                break
    else:
        print("\nNo multi-line remarks found in last column")
        print("\nSample values from last column (first non-empty):")
        for idx, value in df[last_col].items():
            if pd.notna(value) and str(value).strip():
                print(f"  Row {idx}: {str(value)[:100]}")
                print(f"  Type: {type(value)}")
                print(f"  Repr: {repr(str(value)[:100])}")
                break
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
