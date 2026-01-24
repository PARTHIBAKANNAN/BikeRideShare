#!/usr/bin/env python3
"""
Update RideRequest table schema to support ride joining functionality
"""

import sqlite3
import os

def update_ride_request_schema():
    # Database path
    db_path = os.path.join('instance', 'ride_matcher.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Updating RideRequest table schema...")
        
        # Add pickup_location column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE ride_requests ADD COLUMN pickup_location VARCHAR(100)")
            print("✅ Added pickup_location column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ pickup_location column already exists")
            else:
                print(f"⚠️ Error adding pickup_location: {e}")
        
        # Add responded_at column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE ride_requests ADD COLUMN responded_at DATETIME")
            print("✅ Added responded_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ responded_at column already exists")
            else:
                print(f"⚠️ Error adding responded_at: {e}")
        
        # Update default status for existing records
        cursor.execute("UPDATE ride_requests SET status = 'pending' WHERE status = 'active' AND ride_id IS NOT NULL")
        rows_updated = cursor.rowcount
        if rows_updated > 0:
            print(f"✅ Updated {rows_updated} ride join request(s) status to 'pending'")
        
        conn.commit()
        print("✅ RideRequest schema update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_ride_request_schema() 