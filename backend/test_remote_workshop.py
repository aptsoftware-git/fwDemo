from sqlalchemy import create_engine, text
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check total count
    result = conn.execute(text('SELECT COUNT(*) as count FROM remote_workshop'))
    print('Remote Workshop total rows:', result.fetchone()[0])
    
    # Check by sheet
    result = conn.execute(text('SELECT sheet_name, COUNT(*) as count FROM remote_workshop GROUP BY sheet_name'))
    print('Remote Workshop by sheet:')
    for row in result:
        print(f'  {row[0]}: {row[1]} rows')
    
    # Check by dataset
    result = conn.execute(text('''
        SELECT d.tag, rw.sheet_name, COUNT(*) as count 
        FROM remote_workshop rw 
        JOIN datasets d ON d.id = rw.dataset_id 
        GROUP BY d.tag, rw.sheet_name 
        ORDER BY d.tag, rw.sheet_name
    '''))
    print('Remote Workshop by dataset and sheet:')
    for row in result:
        print(f'  {row[0]} - {row[1]}: {row[2]} rows')
