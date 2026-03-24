import requests
from sqlalchemy import create_engine, text
from config import DATABASE_URL

# Test API endpoints
datasets = [
    'November 2025',
    'Local Workshop November 2025',
    'Remote Workshop November 2025',
    'December 2025',
    'Local Workshop December 2025',
    'Remote Workshop December 2025'
]

print("=" * 80)
print("API Endpoint Tests")
print("=" * 80)
for dataset in datasets:
    try:
        r = requests.get(f'http://localhost:8000/api/data/{dataset}')
        result = r.json()
        sheets = result.get('sheets', {})
        sheet_count = {sheet: len(rows) for sheet, rows in sheets.items()}
        print(f'[OK] {dataset:40} | Sheets: {sheet_count}')
    except Exception as e:
        print(f'[ERR] {dataset:40} | Error: {e}')

# Test direct database counts
print("\n" + "=" * 80)
print("Direct Database Counts")
print("=" * 80)
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    # Local Workshop
    result = conn.execute(text('SELECT dataset_id, COUNT(*) FROM local_workshop GROUP BY dataset_id'))
    print("\nLocal Workshop rows by dataset:")
    for row in result:
        print(f'  Dataset {row[0]}: {row[1]} rows')
    
    # Remote Workshop
    result = conn.execute(text('SELECT dataset_id, sheet_name, COUNT(*) FROM remote_workshop GROUP BY dataset_id, sheet_name'))
    print("\nRemote Workshop rows by dataset and sheet:")
    for row in result:
        print(f'  Dataset {row[0]}, Sheet {row[1]}: {row[2]} rows')

