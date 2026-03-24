"""
Migration script to update sheet_name from 'MUA' to 'VOR Spares' in remote_workshop table.

This script handles the sheet name change from MUA to VOR Spares.
"""
from database import SessionLocal, engine
from sqlalchemy import text

def migrate_sheet_name():
    """Update sheet_name from 'MUA' to 'VOR Spares' in remote_workshop table."""
    db = SessionLocal()
    
    try:
        # Check for existing MUA records
        result = db.execute(text("SELECT COUNT(*) FROM remote_workshop WHERE sheet_name = 'MUA'"))
        count = result.scalar()
        print(f"Found {count} records with sheet_name = 'MUA'")
        
        if count > 0:
            # Update MUA to VOR Spares
            db.execute(text("UPDATE remote_workshop SET sheet_name = 'VOR Spares' WHERE sheet_name = 'MUA'"))
            db.commit()
            print(f"Successfully updated {count} records from 'MUA' to 'VOR Spares'")
        else:
            print("No records found with sheet_name = 'MUA'")
        
        # Verify the update
        result = db.execute(text("SELECT COUNT(*) FROM remote_workshop WHERE sheet_name = 'VOR Spares'"))
        vor_count = result.scalar()
        print(f"Total records with sheet_name = 'VOR Spares': {vor_count}")
        
        # Show all distinct sheet names
        result = db.execute(text("SELECT DISTINCT sheet_name FROM remote_workshop ORDER BY sheet_name"))
        sheet_names = [row[0] for row in result.fetchall()]
        print(f"All distinct sheet names in remote_workshop: {sheet_names}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting migration: MUA -> VOR Spares")
    print("=" * 50)
    migrate_sheet_name()
    print("=" * 50)
    print("Migration completed successfully!")
