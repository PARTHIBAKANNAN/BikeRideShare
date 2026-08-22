#!/usr/bin/env python3
"""
Database Reset & Re-seed Script for Neon PostgreSQL
Drops all tables, recreates schema, and seeds fresh demo data.
"""

import sys
import os

# Set UTF-8 encoding support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from models.models import db
from seed_data import seed_database

def reset_database():
    app = create_app('development')
    with app.app_context():
        print("[INFO] Dropping all existing tables in Neon PostgreSQL...")
        db.drop_all()
        print("[OK] All tables dropped.")
        
        print("[INFO] Creating fresh database schema...")
        db.create_all()
        print("[OK] Fresh schema created successfully.")
        
        print("[INFO] Seeding initial clean data...")
        seed_database()
        
        print("\n" + "=" * 60)
        print("🎉 DATABASE RESET AND RE-SEEDED SUCCESSFULLY!")
        print("=" * 60)

if __name__ == '__main__':
    reset_database()
