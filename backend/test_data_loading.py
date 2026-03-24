"""
Test script to verify demo data loading
"""
from pathlib import Path
from services.demo_service import get_file_by_pattern, parse_workshop_sheet, LOCAL_WORKSHOP_SHEETS, REMOTE_WORKSHOP_SHEETS
import os

# Check demo path
DEMO_BASE_PATH = os.getenv('DEMO_BASE_PATH', r'C:\Anu\APT\apt\army\fortwilliam\code\fwDemo\data\FRS_cleaned')
base_path = Path(DEMO_BASE_PATH)

print(f"Base path: {base_path}")
print(f"Base path exists: {base_path.exists()}\n")

# Check November directory
nov_dir = base_path / "Nov" / "Fmn D Nov"
print(f"=== November Directory ===")
print(f"Path: {nov_dir}")
print(f"Exists: {nov_dir.exists()}")

if nov_dir.exists():
    print("\nFiles in directory:")
    for f in nov_dir.iterdir():
        if f.is_file():
            print(f"  - {f.name}")
    
    print("\n--- File Pattern Matching ---")
    # Test formation file
    formation_file = get_file_by_pattern(nov_dir, "2025-D")
    print(f"Formation file (pattern '2025-D'): {formation_file.name if formation_file else 'NOT FOUND'}")
    
    # Test local workshop file
    local_file = get_file_by_pattern(nov_dir, "Local")
    print(f"Local Workshop file (pattern 'Local'): {local_file.name if local_file else 'NOT FOUND'}")
    
    if local_file:
        print(f"\n--- Local Workshop Sheets ---")
        print(f"Expected sheets: {LOCAL_WORKSHOP_SHEETS}")
        for sheet_name in LOCAL_WORKSHOP_SHEETS:
            try:
                df = parse_workshop_sheet(local_file, sheet_name)
                print(f"  ✓ {sheet_name}: {len(df)} rows, columns: {list(df.columns[:5])}...")
            except Exception as e:
                print(f"  ✗ {sheet_name}: Error - {str(e)}")
    
    # Test remote workshop file
    remote_file = get_file_by_pattern(nov_dir, "Remote")
    print(f"\nRemote Workshop file (pattern 'Remote'): {remote_file.name if remote_file else 'NOT FOUND'}")
    
    if remote_file:
        print(f"\n--- Remote Workshop Sheets ---")
        print(f"Expected sheets: {REMOTE_WORKSHOP_SHEETS}")
        for sheet_name in REMOTE_WORKSHOP_SHEETS:
            try:
                df = parse_workshop_sheet(remote_file, sheet_name)
                print(f"  ✓ {sheet_name}: {len(df)} rows, columns: {list(df.columns[:5])}...")
            except Exception as e:
                print(f"  ✗ {sheet_name}: Error - {str(e)}")

# Check December directory
dec_dir = base_path / "Dec" / "Fmn D Dec"
print(f"\n\n=== December Directory ===")
print(f"Path: {dec_dir}")
print(f"Exists: {dec_dir.exists()}")

if dec_dir.exists():
    print("\nFiles in directory:")
    for f in dec_dir.iterdir():
        if f.is_file() and not f.name.startswith('~$'):
            print(f"  - {f.name}")
    
    print("\n--- File Pattern Matching ---")
    # Test formation file
    formation_file = get_file_by_pattern(dec_dir, "2025-D")
    print(f"Formation file (pattern '2025-D'): {formation_file.name if formation_file else 'NOT FOUND'}")
    
    # Test local workshop file
    local_file = get_file_by_pattern(dec_dir, "Local")
    print(f"Local Workshop file (pattern 'Local'): {local_file.name if local_file else 'NOT FOUND'}")
    
    if local_file:
        print(f"\n--- Local Workshop Sheets ---")
        print(f"Expected sheets: {LOCAL_WORKSHOP_SHEETS}")
        for sheet_name in LOCAL_WORKSHOP_SHEETS:
            try:
                df = parse_workshop_sheet(local_file, sheet_name)
                print(f"  ✓ {sheet_name}: {len(df)} rows, columns: {list(df.columns[:5])}...")
            except Exception as e:
                print(f"  ✗ {sheet_name}: Error - {str(e)}")
    
    # Test remote workshop file
    remote_file = get_file_by_pattern(dec_dir, "Remote")
    print(f"\nRemote Workshop file (pattern 'Remote'): {remote_file.name if remote_file else 'NOT FOUND'}")
    
    if remote_file:
        print(f"\n--- Remote Workshop Sheets ---")
        print(f"Expected sheets: {REMOTE_WORKSHOP_SHEETS}")
        for sheet_name in REMOTE_WORKSHOP_SHEETS:
            try:
                df = parse_workshop_sheet(remote_file, sheet_name)
                print(f"  ✓ {sheet_name}: {len(df)} rows, columns: {list(df.columns[:5])}...")
            except Exception as e:
                print(f"  ✗ {sheet_name}: Error - {str(e)}")
