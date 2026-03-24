from sqlalchemy import create_engine, text
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)

print("=" * 80)
print("LOCAL WORKSHOP - Distinct Units")
print("=" * 80)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT dataset_id, unit, COUNT(*) as row_count 
        FROM local_workshop 
        GROUP BY dataset_id, unit 
        ORDER BY dataset_id, unit
    """))
    for row in result:
        print(f"Dataset {row[0]}: Unit '{row[1]}' - {row[2]} rows")

print("\n" + "=" * 80)
print("REMOTE WORKSHOP - Distinct Units")
print("=" * 80)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT dataset_id, unit, COUNT(*) as row_count 
        FROM remote_workshop 
        GROUP BY dataset_id, unit 
        ORDER BY dataset_id, unit
    """))
    for row in result:
        print(f"Dataset {row[0]}: Unit '{row[1]}' - {row[2]} rows")

print("\n" + "=" * 80)
print("Checking Formation column from row_data")
print("=" * 80)
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT DISTINCT row_data->>'Formation' as formation, row_data->>'Units' as unit
        FROM local_workshop 
        LIMIT 10
    """))
    print("\nLocal Workshop sample:")
    for row in result:
        print(f"  Formation: {row[0]}, Units: {row[1]}")
    
    result = conn.execute(text("""
        SELECT DISTINCT row_data->>'Formation' as formation, row_data->>'Units' as unit
        FROM remote_workshop 
        LIMIT 10
    """))
    print("\nRemote Workshop sample:")
    for row in result:
        print(f"  Formation: {row[0]}, Units: {row[1]}")
