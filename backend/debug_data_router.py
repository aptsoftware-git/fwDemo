"""Debug script to test data_router logic"""
from database import SessionLocal
from models import Dataset, LocalWorkshop

db = SessionLocal()

# Find dataset
tag = "Local Workshop November 2025"
dataset = db.query(Dataset).filter(Dataset.tag == tag).first()

if not dataset:
    print(f"Dataset not found: {tag}")
else:
    print(f"Dataset found: {dataset.tag} (ID: {dataset.id})")
    
    # Query LocalWorkshop table
    query = db.query(LocalWorkshop).filter(LocalWorkshop.dataset_id == dataset.id)
    workshop_records = query.all()
    
    print(f"\nTotal records: {len(workshop_records)}")
    
    # Organize data by sheet name
    sheets_temp = {}
    for record in workshop_records:
        print(f"  Record - Sheet: {record.sheet_name}, Unit: {record.unit}, Category: {record.category}")
        if record.sheet_name not in sheets_temp:
            sheets_temp[record.sheet_name] = []
        sheets_temp[record.sheet_name].append(record.row_data)
    
    print(f"\nSheets organized:")
    for sheet_name, data in sheets_temp.items():
        print(f"  {sheet_name}: {len(data)} rows")
        if len(data) > 0:
            print(f"    Sample keys: {list(data[0].keys())[:5]}")

db.close()
