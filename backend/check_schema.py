"""Check database schema for local_workshop table"""
from database import engine
from sqlalchemy import text

conn = engine.connect()

# Check local_workshop columns
print("=== LOCAL WORKSHOP TABLE SCHEMA ===")
result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'local_workshop' ORDER BY ordinal_position"))
columns = [(row[0], row[1]) for row in result]
for col_name, col_type in columns:
    print(f"  {col_name}: {col_type}")

# Check row count
result = conn.execute(text("SELECT COUNT(*) FROM local_workshop"))
count = result.fetchone()[0]
print(f"\nLocal Workshop row count: {count}")

# Check remote_workshop columns
print("\n=== REMOTE WORKSHOP TABLE SCHEMA ===")
result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'remote_workshop' ORDER BY ordinal_position"))
columns = [(row[0], row[1]) for row in result]
for col_name, col_type in columns:
    print(f"  {col_name}: {col_type}")

# Check row count
result = conn.execute(text("SELECT COUNT(*) FROM remote_workshop"))
count = result.fetchone()[0]
print(f"\nRemote Workshop row count: {count}")

conn.close()
