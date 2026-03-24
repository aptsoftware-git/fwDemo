"""
Check remote_workshop table contents
"""
from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Get count by sheet_name
    result = db.execute(text("SELECT sheet_name, COUNT(*) as cnt FROM remote_workshop GROUP BY sheet_name ORDER BY sheet_name"))
    rows = result.fetchall()
    
    print("Remote Workshop data by sheet:")
    total = 0
    for row in rows:
        print(f"  {row[0]}: {row[1]} rows")
        total += row[1]
    
    print(f"\nTotal: {total} rows")
    
    if total > 0:
        # Show sample Control date values
        result = db.execute(text("SELECT DISTINCT \"Control date\" FROM remote_workshop WHERE \"Control date\" IS NOT NULL LIMIT 10"))
        control_dates = [r[0] for r in result.fetchall()]
        print(f"\nSample Control date values: {control_dates}")
        
finally:
    db.close()
