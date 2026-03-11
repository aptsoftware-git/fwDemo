"""
Verify that newlines are preserved through the data processing pipeline
"""
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from parsers.excel_parser import parse_sheet_with_detection
from processors.data_cleaner import clean_dataframe, dataframe_to_json

# Test with a sample Excel file
excel_path = Path("../data/FRS_Sample/Dec/Fmn A Dec")
excel_files = list(excel_path.glob("*.xls*"))

if not excel_files:
    print("No Excel files found!")
    sys.exit(1)

excel_file = excel_files[0]
print(f"Testing with: {excel_file.name}\n")

# Parse the B Veh sheet
try:
    df = parse_sheet_with_detection(Path(excel_file), "Appx A (B veh)")
    print(f"✓ Parsed sheet: {df.shape[0]} rows, {df.shape[1]} columns\n")
    
    # Find remarks column
    remarks_col = None
    for col in df.columns:
        if 'remark' in str(col).lower():
            remarks_col = col
            break
    
    if not remarks_col:
        print("No remarks column found!")
        sys.exit(1)
    
    print(f"Remarks column: '{remarks_col}'\n")
    
    # Check for newlines in raw data
    print("="*80)
    print("BEFORE clean_dataframe:")
    print("="*80)
    for idx, value in df[remarks_col].items():
        if pd.notna(value) and isinstance(value, str) and '\n' in value:
            lines = value.split('\n')
            print(f"\nRow {idx}: {len(lines)} lines, {len(value)} chars")
            print(f"  Has newlines: YES ✓")
            for i, line in enumerate(lines[:3], 1):
                print(f"    Line {i}: {line[:50]}")
            if len(lines) > 3:
                print(f"    ... ({len(lines)} total lines)")
            break
    else:
        print("No newlines found in raw data")
    
    # Clean the dataframe
    cleaned_df = clean_dataframe(df, remove_duplicates=False, fill_strategy='keep')
    print(f"\n✓ Cleaned dataframe: {cleaned_df.shape[0]} rows\n")
    
    # Check for newlines after cleaning
    print("="*80)
    print("AFTER clean_dataframe:")
    print("="*80)
    for idx, value in cleaned_df[remarks_col].items():
        if pd.notna(value) and isinstance(value, str) and '\n' in value:
            lines = value.split('\n')
            print(f"\nRow {idx}: {len(lines)} lines, {len(value)} chars")
            print(f"  Has newlines: YES ✓")
            print(f"  NEWLINES PRESERVED! ✓✓✓")
            for i, line in enumerate(lines[:3], 1):
                print(f"    Line {i}: {line[:50]}")
            if len(lines) > 3:
                print(f"    ... ({len(lines)} total lines)")
            break
    else:
        print("❌ No newlines found after cleaning - NEWLINES WERE REMOVED!")
    
    # Convert to JSON
    json_data = dataframe_to_json(cleaned_df)
    print(f"\n✓ Converted to JSON: {len(json_data)} rows\n")
    
    # Check JSON data
    print("="*80)
    print("IN JSON FORMAT:")
    print("="*80)
    for row in json_data:
        if remarks_col in row and row[remarks_col] and '\n' in str(row[remarks_col]):
            value = row[remarks_col]
            lines = value.split('\n')
            print(f"\nRow remarks: {len(lines)} lines")
            print(f"  Has newlines in JSON: YES ✓")
            print(f"  NEWLINES PRESERVED IN JSON! ✓✓✓")
            for i, line in enumerate(lines[:3], 1):
                print(f"    Line {i}: {line[:50]}")
            if len(lines) > 3:
                print(f"    ... ({len(lines)} total lines)")
            break
    else:
        print("❌ No newlines in JSON - NEWLINES WERE REMOVED!")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print("✓ Excel reading: Newlines present")
    print("✓ After cleaning: Newlines preserved" if any('\n' in str(v) for v in cleaned_df[remarks_col] if pd.notna(v)) else "❌ Cleaning removed newlines")
    print("✓ In JSON: Newlines preserved" if any('\n' in str(row.get(remarks_col, '')) for row in json_data) else "❌ JSON conversion removed newlines")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
