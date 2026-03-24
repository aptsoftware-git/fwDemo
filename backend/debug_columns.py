"""
Debug script to check column names in A Vehicle data.
"""
from database import SessionLocal
from models import Dataset, Unit, SheetData

db = SessionLocal()

try:
    # Check November 2025
    print("=" * 80)
    print("NOVEMBER 2025 - A VEHICLE DATA COLUMNS")
    print("=" * 80)
    nov_ds = db.query(Dataset).filter(Dataset.tag == "November 2025").first()
    if nov_ds:
        units = db.query(Unit).filter(Unit.dataset_id == nov_ds.id).all()
        for unit in units:
            sheets = db.query(SheetData).filter(
                SheetData.unit_id == unit.id,
                SheetData.sheet_type == "APPX_A_AVEH"
            ).all()
            for sheet in sheets:
                if sheet.row_data and len(sheet.row_data) > 0:
                    print(f"\nSheet found with {len(sheet.row_data)} rows")
                    print(f"Columns: {list(sheet.row_data[0].keys())}")
                    print(f"\nFirst row sample:")
                    for key, value in list(sheet.row_data[0].items())[:10]:
                        print(f"  {key}: {value}")
    else:
        print("November 2025 dataset NOT FOUND")
    
    # Check December 2025
    print("\n" + "=" * 80)
    print("DECEMBER 2025 - A VEHICLE DATA COLUMNS")
    print("=" * 80)
    dec_ds = db.query(Dataset).filter(Dataset.tag == "December 2025").first()
    if dec_ds:
        units = db.query(Unit).filter(Unit.dataset_id == dec_ds.id).all()
        for unit in units:
            sheets = db.query(SheetData).filter(
                SheetData.unit_id == unit.id,
                SheetData.sheet_type == "APPX_A_AVEH"
            ).all()
            for sheet in sheets:
                if sheet.row_data and len(sheet.row_data) > 0:
                    print(f"\nSheet found with {len(sheet.row_data)} rows")
                    print(f"Columns: {list(sheet.row_data[0].keys())}")
                    print(f"\nFirst row sample:")
                    for key, value in list(sheet.row_data[0].items())[:10]:
                        print(f"  {key}: {value}")
    else:
        print("December 2025 dataset NOT FOUND")
    
finally:
    db.close()
