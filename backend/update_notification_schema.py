#!/usr/bin/env python3
"""
Update database schema to add notifications table
"""

import sqlite3
import os

def update_notification_schema():
    # Database path
    db_path = os.path.join('instance', 'ride_matcher.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Adding notifications table...")
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                ride_id INTEGER,
                ride_request_id INTEGER,
                related_user_id INTEGER,
                is_read BOOLEAN DEFAULT 0,
                is_actioned BOOLEAN DEFAULT 0,
                action_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                read_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (ride_id) REFERENCES rides (id),
                FOREIGN KEY (ride_request_id) REFERENCES ride_requests (id),
                FOREIGN KEY (related_user_id) REFERENCES users (id)
            )
        """)
        
        print("✅ Created notifications table")
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)")
        
        print("✅ Created indexes for notifications table")
        
        conn.commit()
        print("✅ Notification schema update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_notification_schema() 