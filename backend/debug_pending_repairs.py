from database import engine, SessionLocal
from models import Dataset, LocalWorkshop
from datetime import datetime, timezone

db = SessionLocal()

# Find Local Workshop December 2025 dataset
dataset = db.query(Dataset).filter(
    Dataset.tag.like("%Local Workshop%"),
    Dataset.tag.like("%December%"),
    Dataset.tag.like("%2025%")
).first()

print(f'=== Dataset Info ===')
print(f'Dataset ID: {dataset.id if dataset else "Not found"}')
print(f'Dataset Tag: {dataset.tag if dataset else "Not found"}')
print()

if dataset:
    # Query Local Workshop data for FR and SPARES sheets
    sheet_names = ["FR", "SPARES"]
    local_data = db.query(LocalWorkshop).filter(
        LocalWorkshop.dataset_id == dataset.id,
        LocalWorkshop.sheet_name.in_(sheet_names)
    ).all()
    
    print(f'Total records: {len(local_data)}')
    print()
    
    current_date = datetime.now(timezone.utc)
    print(f'Current date: {current_date}')
    print()
    
    result = []
    serial_no = 1
    
    for i, record in enumerate(local_data[:5]):  # Check first 5 for debugging
        row_data = record.row_data
        
        print(f'=== Record {i+1} ===')
        print(f'Sheet: {record.sheet_name} | Unit: {record.unit} | Category: {record.category}')
        
        # Get repair status - check various possible column names
        repair_status_key = None
        repair_status = None
        for key in row_data.keys():
            if 'repair' in key.lower() and 'status' in key.lower():
                repair_status_key = key
                repair_status = row_data.get(key, "")
                break
        
        print(f'Repair Status Key Found: {repr(repair_status_key)}')
        print(f'Repair Status Value: {repr(repair_status)}')
        
        # Filter: Repair Status is "No" or "NO"
        if repair_status and str(repair_status).strip().upper() in ["NO", "N"]:
            print('✓ Repair Status is NO')
            
            # Get defect date
            defect_dt_str = row_data.get("Defect dt", "")
            print(f'Defect dt: {defect_dt_str}')
            
            # Calculate pending days
            pending_days = None
            if defect_dt_str:
                try:
                    # Parse the defect date (ISO format from database)
                    if isinstance(defect_dt_str, str):
                        defect_dt = datetime.fromisoformat(defect_dt_str.replace('Z', '+00:00'))
                    else:
                        defect_dt = defect_dt_str
                    
                    # Calculate difference in days
                    if defect_dt:
                        delta = current_date - defect_dt.replace(tzinfo=timezone.utc) if defect_dt.tzinfo is None else current_date - defect_dt
                        pending_days = delta.days
                        print(f'Pending days: {pending_days}')
                        
                        if pending_days > 90:
                            print('✓ Pending days > 90. This record SHOULD be included!')
                            serial_no += 1
                        else:
                            print('✗ Pending days <= 90. Filtered out.')
                except Exception as e:
                    print(f'Error parsing defect date: {e}')
        else:
            print(f'✗ Repair Status not "NO". Value: {repr(repair_status)}, Upper: {repr(str(repair_status).strip().upper() if repair_status else None)}')
        
        print()

db.close()
