"""
Script to recreate database tables.
WARNING: This will delete all existing data!
"""
from database import Base, engine, drop_db, init_db
from models import Dataset, Unit, SheetData, LocalWorkshop, RemoteWorkshop

def recreate_database():
    """Drop all tables and recreate them with the current schema."""
    print("WARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    print("\nDropping all tables...")
    drop_db()
    
    print("\nCreating tables with new schema...")
    init_db()
    
    print("\n✅ Database recreated successfully!")
    print("All tables have been created with the latest schema.")

if __name__ == "__main__":
    recreate_database()
