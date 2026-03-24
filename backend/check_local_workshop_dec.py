from database import engine
from sqlalchemy import text

conn = engine.connect()

# Check for Local Workshop December 2025 dataset
result = conn.execute(text("""
    SELECT d.id, d.tag, COUNT(lw.id) as count 
    FROM datasets d 
    LEFT JOIN local_workshop lw ON d.id = lw.dataset_id 
    WHERE d.tag LIKE '%Local Workshop%' 
      AND d.tag LIKE '%December%' 
      AND d.tag LIKE '%2025%' 
    GROUP BY d.id, d.tag
"""))

rows = list(result)
print('=== Local Workshop December 2025 Datasets ===')
if rows:
    for row in rows:
        print(f'Dataset ID: {row[0]}')
        print(f'Tag: {row[1]}')
        print(f'Total rows: {row[2]}')
        print()
else:
    print('No datasets found')
    print()

# Check a sample of Local Workshop December data with repair status
if rows and rows[0][2] > 0:
    dataset_id = rows[0][0]
    result2 = conn.execute(text(f"""
        SELECT 
            sheet_name,
            unit,
            category,
            row_data->>'Repair Status (Yes/ No)' as repair_status,
            row_data->>'Defect dt' as defect_dt
        FROM local_workshop 
        WHERE dataset_id = {dataset_id}
        LIMIT 10
    """))
    
    print('=== Sample Local Workshop December Data ===')
    for row in result2:
        print(f'Sheet: {row[0]} | Unit: {row[1]} | Category: {row[2]}')
        print(f'  Repair Status: {row[3]} | Defect dt: {row[4]}')
        print()

conn.close()
