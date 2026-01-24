#!/usr/bin/env python3
"""
Update database schema for comprehensive admin functionality
Adds license verification, user flagging, and reports table
"""

import sqlite3
import os

def update_database_schema():
    """Add all new admin-related fields and tables"""
    
    db_path = 'instance/ride_matcher.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the app first to create the database.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Updating database schema for admin functionality...")
        print("=" * 60)
        
        # 1. Add license verification fields to users table
        print("➕ Adding license verification fields to users table...")
        
        # Check existing columns first
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # License verification fields
        license_fields = [
            ('license_number', 'VARCHAR(20)'),
            ('license_image_url', 'VARCHAR(255)'),
            ('license_verified', 'BOOLEAN DEFAULT 0'),
            ('license_verification_status', 'VARCHAR(20) DEFAULT "pending"'),
            ('license_rejection_reason', 'TEXT')
        ]
        
        for field_name, field_type in license_fields:
            if field_name not in existing_columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
                print(f"   ✅ Added {field_name}")
            else:
                print(f"   ⚠️ {field_name} already exists")
        
        # 2. Add user flagging fields to users table
        print("\n➕ Adding user flagging fields to users table...")
        
        flagging_fields = [
            ('is_flagged', 'BOOLEAN DEFAULT 0'),
            ('flag_reason', 'TEXT'),
            ('flagged_by_admin', 'INTEGER'),
            ('flagged_at', 'DATETIME')
        ]
        
        for field_name, field_type in flagging_fields:
            if field_name not in existing_columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
                print(f"   ✅ Added {field_name}")
            else:
                print(f"   ⚠️ {field_name} already exists")
        
        # 3. Create reports table if it doesn't exist
        print("\n➕ Creating reports table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                reported_user_id INTEGER,
                reported_ride_id INTEGER,
                report_type VARCHAR(50) NOT NULL,
                report_category VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                evidence_urls TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(10) DEFAULT 'medium',
                assigned_admin_id INTEGER,
                admin_notes TEXT,
                resolution_action VARCHAR(100),
                resolved_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reporter_id) REFERENCES users (id),
                FOREIGN KEY (reported_user_id) REFERENCES users (id),
                FOREIGN KEY (reported_ride_id) REFERENCES rides (id)
            )
        """)
        print("   ✅ Reports table created/verified")
        
        # 4. Add bike verification status update (ensure is_verified exists)
        print("\n➕ Verifying bikes table has verification fields...")
        
        cursor.execute("PRAGMA table_info(bikes)")
        bike_columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_verified' not in bike_columns:
            cursor.execute("ALTER TABLE bikes ADD COLUMN is_verified BOOLEAN DEFAULT 0")
            print("   ✅ Added is_verified to bikes")
        else:
            print("   ⚠️ is_verified already exists in bikes")
        
        # 5. Create indexes for better performance
        print("\n➕ Creating indexes for performance...")
        
        indexes = [
            ("idx_users_license_status", "CREATE INDEX IF NOT EXISTS idx_users_license_status ON users(license_verification_status)"),
            ("idx_users_flagged", "CREATE INDEX IF NOT EXISTS idx_users_flagged ON users(is_flagged)"),
            ("idx_reports_status", "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)"),
            ("idx_reports_reporter", "CREATE INDEX IF NOT EXISTS idx_reports_reporter ON reports(reporter_id)"),
            ("idx_reports_reported_user", "CREATE INDEX IF NOT EXISTS idx_reports_reported_user ON reports(reported_user_id)"),
            ("idx_bikes_verified", "CREATE INDEX IF NOT EXISTS idx_bikes_verified ON bikes(is_verified)")
        ]
        
        for index_name, index_sql in indexes:
            cursor.execute(index_sql)
            print(f"   ✅ Created {index_name}")
        
        # 6. Verify schema updates
        print("\n🔍 Verifying schema updates...")
        
        # Check users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        required_user_fields = [
            'license_number', 'license_verified', 'license_verification_status',
            'is_flagged', 'flag_reason', 'flagged_by_admin', 'flagged_at'
        ]
        
        missing_user_fields = [field for field in required_user_fields if field not in user_columns]
        if missing_user_fields:
            print(f"   ❌ Missing user fields: {missing_user_fields}")
        else:
            print("   ✅ All user fields present")
        
        # Check reports table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
        if cursor.fetchone():
            print("   ✅ Reports table exists")
        else:
            print("   ❌ Reports table missing")
        
        # Check bikes table
        cursor.execute("PRAGMA table_info(bikes)")
        bike_columns = [column[1] for column in cursor.fetchall()]
        if 'is_verified' in bike_columns:
            print("   ✅ Bikes verification field present")
        else:
            print("   ❌ Bikes verification field missing")
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print("\n🎉 Database schema updated successfully!")
        print("\n📊 New Admin Features Available:")
        print("   • License verification workflow")
        print("   • User flagging and suspension system")
        print("   • Comprehensive reporting system")
        print("   • Bike verification approvals")
        print("   • Enhanced admin dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        return False

def display_schema_summary():
    """Display a summary of the current database schema"""
    db_path = 'instance/ride_matcher.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📋 Database Schema Summary:")
        print("=" * 60)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n🗃️ Table: {table_name}")
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for column in columns:
                col_name = column[1]
                col_type = column[2]
                is_nullable = "NULL" if column[3] == 0 else "NOT NULL"
                default_value = f" DEFAULT {column[4]}" if column[4] else ""
                print(f"   • {col_name}: {col_type} {is_nullable}{default_value}")
        
        # Count records in each table
        print(f"\n📊 Record Counts:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   • {table_name}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading schema: {e}")

if __name__ == "__main__":
    print("🔧 Admin Database Schema Update")
    print("=" * 60)
    
    success = update_database_schema()
    
    if success:
        print("\n✅ Schema update completed successfully!")
        print("You can now restart your Flask app to use the new admin features.")
        
        # Show schema summary
        display_schema_summary()
    else:
        print("\n❌ Schema update failed!")
        print("Please check the error messages above.") 