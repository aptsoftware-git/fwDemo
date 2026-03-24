"""
Migration script to add sheet_name column to local_workshop table
"""
from database import engine
from sqlalchemy import text

def migrate():
    conn = engine.connect()
    trans = conn.begin()
    
    try:
        print("Adding sheet_name column to local_workshop table...")
        
        # Add the column
        conn.execute(text("""
            ALTER TABLE local_workshop 
            ADD COLUMN sheet_name VARCHAR(50)
        """))
        
        # Update existing rows to have 'FR' as default (if any exist)
        conn.execute(text("""
            UPDATE local_workshop 
            SET sheet_name = 'FR' 
            WHERE sheet_name IS NULL
        """))
        
        # Make the column non-nullable
        conn.execute(text("""
            ALTER TABLE local_workshop 
            ALTER COLUMN sheet_name SET NOT NULL
        """))
        
        # Add index
        conn.execute(text("""
            CREATE INDEX ix_local_workshop_sheet_name 
            ON local_workshop(sheet_name)
        """))
        
        trans.commit()
        print("✓ Migration completed successfully!")
        print("  - Added sheet_name column")
        print("  - Set NOT NULL constraint")
        print("  - Created index")
        
    except Exception as e:
        trans.rollback()
        print(f"✗ Migration failed: {str(e)}")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
