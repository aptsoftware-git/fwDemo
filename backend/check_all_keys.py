from database import engine
from sqlalchemy import text

conn = engine.connect()

# Get all unique keys from Local Workshop December 2025
result = conn.execute(text("""
    SELECT DISTINCT jsonb_object_keys(row_data) as key_name
    FROM local_workshop 
    WHERE dataset_id = (
        SELECT id FROM datasets 
        WHERE tag LIKE '%Local Workshop%' 
          AND tag LIKE '%December%' 
          AND tag LIKE '%2025%'
    )
    ORDER BY key_name
"""))

print('=== All column names in Local Workshop December row_data ===')
for row in result:
    key = row[0]
    # Show as raw repr to see any hidden characters
    print(f'{repr(key)}')

conn.close()
