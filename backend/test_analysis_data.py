"""
Test script to check if A Vehicle data exists for analysis.
"""
from database import SessionLocal
from models import Dataset, Unit, SheetData

db = SessionLocal()

try:
    # Check datasets
    print("=" * 80)
    print("DATASETS")
    print("=" * 80)
    datasets = db.query(Dataset).all()
    for ds in datasets:
        print(f"ID: {ds.id}, Tag: {ds.tag}")
    
    # Check November 2025
    print("\n" + "=" * 80)
    print("NOVEMBER 2025 - A VEHICLE DATA")
    print("=" * 80)
    nov_ds = db.query(Dataset).filter(Dataset.tag == "November 2025").first()
    if nov_ds:
        print(f"Dataset found: {nov_ds.id}")
        units = db.query(Unit).filter(Unit.dataset_id == nov_ds.id).all()
        print(f"Units: {len(units)}")
        for unit in units:
            print(f"  Unit ID: {unit.id}, Name: {unit.unit_name}")
            sheets = db.query(SheetData).filter(SheetData.unit_id == unit.id).all()
            print(f"  Sheets: {len(sheets)}")
            for sheet in sheets:
                print(f"    Sheet type: {sheet.sheet_type}, Rows: {len(sheet.row_data) if sheet.row_data else 0}")
                if sheet.sheet_type == "APPX_A_AVEH" and sheet.row_data:
                    print(f"    First row sample: {list(sheet.row_data[0].keys())[:5] if sheet.row_data else 'N/A'}")
    else:
        print("November 2025 dataset NOT FOUND")
    
    # Check December 2025
    print("\n" + "=" * 80)
    print("DECEMBER 2025 - A VEHICLE DATA")
    print("=" * 80)
    dec_ds = db.query(Dataset).filter(Dataset.tag == "December 2025").first()
    if dec_ds:
        print(f"Dataset found: {dec_ds.id}")
        units = db.query(Unit).filter(Unit.dataset_id == dec_ds.id).all()
        print(f"Units: {len(units)}")
        for unit in units:
            print(f"  Unit ID: {unit.id}, Name: {unit.unit_name}")
            sheets = db.query(SheetData).filter(SheetData.unit_id == unit.id).all()
            print(f"  Sheets: {len(sheets)}")
            for sheet in sheets:
                print(f"    Sheet type: {sheet.sheet_type}, Rows: {len(sheet.row_data) if sheet.row_data else 0}")
                if sheet.sheet_type == "APPX_A_AVEH" and sheet.row_data:
                    print(f"    First row sample: {list(sheet.row_data[0].keys())[:5] if sheet.row_data else 'N/A'}")
    else:
        print("December 2025 dataset NOT FOUND")
    
finally:
    db.close()
