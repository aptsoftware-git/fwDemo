"""Check if Local Workshop data is in database"""
from database import engine
from sqlalchemy import text

conn = engine.connect()

print("=== LOCAL WORKSHOP DATA CHECK ===\n")

# Check total rows
result = conn.execute(text("SELECT COUNT(*) FROM local_workshop"))
total = result.fetchone()[0]
print(f"Total Local Workshop rows: {total}")

if total > 0:
    # Check by dataset
    result = conn.execute(text("""
        SELECT d.tag, lw.sheet_name, COUNT(*) as row_count
        FROM local_workshop lw
        JOIN datasets d ON lw.dataset_id = d.id
        GROUP BY d.tag, lw.sheet_name
        ORDER BY d.tag, lw.sheet_name
    """))
    
    print("\nBreakdown by dataset and sheet:")
    for row in result:
        print(f"  {row[0]} - {row[1]}: {row[2]} rows")
    
    # Sample data from first record
    result = conn.execute(text("""
        SELECT d.tag, lw.sheet_name, lw.unit, lw.category
        FROM local_workshop lw
        JOIN datasets d ON lw.dataset_id = d.id
        LIMIT 5
    """))
    
    print("\nSample records:")
    for row in result:
        print(f"  Dataset: {row[0]}, Sheet: {row[1]}, Unit: {row[2]}, Category: {row[3]}")
else:
    print("\n⚠ No data found in local_workshop table!")
    print("   You need to:")
    print("   1. Restart the backend server")
    print("   2. Click 'Clear' in the web app")
    print("   3. Click 'Load' in the web app")

print("\n=== REMOTE WORKSHOP DATA CHECK ===\n")

# Check remote workshop too
result = conn.execute(text("SELECT COUNT(*) FROM remote_workshop"))
total = result.fetchone()[0]
print(f"Total Remote Workshop rows: {total}")

if total > 0:
    result = conn.execute(text("""
        SELECT d.tag, rw.sheet_name, COUNT(*) as row_count
        FROM remote_workshop rw
        JOIN datasets d ON rw.dataset_id = d.id
        GROUP BY d.tag, rw.sheet_name
        ORDER BY d.tag, rw.sheet_name
    """))
    
    print("\nBreakdown by dataset and sheet:")
    for row in result:
        print(f"  {row[0]} - {row[1]}: {row[2]} rows")

conn.close()
