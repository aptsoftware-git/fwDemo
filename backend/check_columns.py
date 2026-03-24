from database import engine
from sqlalchemy import text
import json

conn = engine.connect()

# Get one row from Local Workshop December 2025
result = conn.execute(text("""
    SELECT 
        sheet_name,
        unit,
        category,
        row_data
    FROM local_workshop 
    WHERE dataset_id = (
        SELECT id FROM datasets 
        WHERE tag LIKE '%Local Workshop%' 
          AND tag LIKE '%December%' 
          AND tag LIKE '%2025%'
    )
    LIMIT 1
"""))

row = result.fetchone()
if row:
    print('=== Sample Local Workshop December Row ===')
    print(f'Sheet: {row[0]}')
    print(f'Unit: {row[1]}')
    print(f'Category: {row[2]}')
    print('\nAvailable columns in row_data:')
    row_data = row[3]
    for key in sorted(row_data.keys()):
        value = row_data[key]
        if len(str(value)) > 50:
            value = str(value)[:50] + '...'
        print(f'  {key}: {value}')
else:
    print('No data found')

conn.close()
