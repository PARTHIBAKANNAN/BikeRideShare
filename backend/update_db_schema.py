#!/usr/bin/env python3
"""
Update database schema to add manufacture_year column to bikes table
"""

import sqlite3
import os

def update_database_schema():
    """Add manufacture_year column to bikes table"""
    
    db_path = 'instance/ride_matcher.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the app first to create the database.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if manufacture_year column already exists
        cursor.execute("PRAGMA table_info(bikes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'manufacture_year' in columns:
            print("✅ manufacture_year column already exists in bikes table")
        else:
            print("➕ Adding manufacture_year column to bikes table...")
            cursor.execute("ALTER TABLE bikes ADD COLUMN manufacture_year INTEGER")
            print("✅ manufacture_year column added successfully")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("🎉 Database schema updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Updating database schema...")
    print("=" * 50)
    
    success = update_database_schema()
    
    if success:
        print("\n✅ Schema update completed!")
        print("You can now restart your Flask app.")
    else:
        print("\n❌ Schema update failed!")
        print("Please check the error messages above.") 