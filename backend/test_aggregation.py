"""
Test script to debug aggregation issue
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL, SHEET_TYPE_ORDER
from models import Dataset, Unit, SheetData
from processors.data_cleaner import aggregate_by_category

# Create database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Find the dataset
    tag = "Fmn December 2025"
    dataset = db.query(Dataset).filter(Dataset.tag == tag).first()
    if not dataset:
        print(f"Dataset not found: {tag}")
        sys.exit(1)
    
    print(f"Found dataset: {dataset.tag}")
    print(f"Dataset ID: {dataset.id}")
    
    # Get sheet data for all units
    query = db.query(SheetData).join(Unit).filter(Unit.dataset_id == dataset.id)
    sheet_data_records = query.all()
    
    print(f"\nFound {len(sheet_data_records)} sheet_data records")
    
    # Organize by sheet type
    sheets_temp = {}
    for record in sheet_data_records:
        if record.sheet_type not in sheets_temp:
            sheets_temp[record.sheet_type] = []
        
        print(f"\nRecord ID: {record.id}")
        print(f"  Sheet type: {record.sheet_type}")
        print(f"  row_data type: {type(record.row_data)}")
        print(f"  row_data length: {len(record.row_data) if record.row_data else 0}")
        
        if record.row_data:
            print(f"  First row type: {type(record.row_data[0])}")
            print(f"  First row keys: {list(record.row_data[0].keys()) if isinstance(record.row_data[0], dict) else 'NOT A DICT'}")
            print(f"  First row sample: {str(record.row_data[0])[:200]}")
        
        sheets_temp[record.sheet_type].extend(record.row_data)
    
    # Try aggregation on each sheet type
    print("\n" + "="*80)
    print("TESTING AGGREGATION")
    print("="*80)
    
    for sheet_type, rows in sheets_temp.items():
        print(f"\nAggregating {sheet_type}:")
        print(f"  Input: {len(rows)} rows")
        
        try:
            aggregated = aggregate_by_category(rows, use_ai_for_remarks=False)
            print(f"  Output: {len(aggregated)} rows")
            print(f"  SUCCESS!")
            
            # Show first aggregated row
            if aggregated:
                print(f"  First aggregated row keys: {list(aggregated[0].keys())}")
                print(f"  First aggregated row: {aggregated[0]}")
                
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    
finally:
    db.close()
