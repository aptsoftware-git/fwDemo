"""
Script to inspect Remote Workshop data structure
"""
from sqlalchemy import create_engine, text
from config import DATABASE_URL
import json

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Get column names from Eng sheet
    result = conn.execute(text("SELECT row_data FROM remote_workshop WHERE sheet_name = 'Eng' LIMIT 1"))
    row = result.fetchone()
    
    if row:
        columns = list(row[0].keys())
        print("Eng sheet columns:")
        print(json.dumps(columns, indent=2))
        print("\n\nSample data:")
        print(json.dumps(row[0], indent=2, default=str))
    else:
        print("No Eng data found")
    
    # Get column names from EOA Spares sheet
    result = conn.execute(text("SELECT row_data FROM remote_workshop WHERE sheet_name = 'EOA Spares' LIMIT 1"))
    row = result.fetchone()
    
    if row:
        print("\n\nEOA Spares sheet columns:")
        columns = list(row[0].keys())
        print(json.dumps(columns, indent=2))
    else:
        print("\nNo EOA Spares data found")
    
    # Get column names from MUA sheet
    result = conn.execute(text("SELECT row_data FROM remote_workshop WHERE sheet_name = 'MUA' LIMIT 1"))
    row = result.fetchone()
    
    if row:
        print("\n\nMUA sheet columns:")
        columns = list(row[0].keys())
        print(json.dumps(columns, indent=2))
    else:
        print("\nNo MUA data found")
