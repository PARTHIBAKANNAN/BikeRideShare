#!/usr/bin/env python3
"""
Seed script to initialize Admin account in Neon PostgreSQL.
No hardcoded rides are created, keeping the database clean for real operations.
"""

import sys
import os

# Set UTF-8 encoding support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from models.models import db, User, Bike, Ride, RideRequest
from services.auth_service import AuthService

def seed_database():
    app = create_app('development')
    with app.app_context():
        print("[INFO] Checking admin account...")
        
        # Admin credentials specified by user: admin@gmail.com / Admin@7781
        admin_email = "admin@gmail.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin_data = {
                'name': 'System Administrator',
                'phone': '+919876543210',
                'email': admin_email,
                'password': 'Admin@7781',
                'work_location': 'Olympia Tech Park',
                'home_location': 'Maduravoyal'
            }
            AuthService.register_user(admin_data)
            admin = User.query.filter_by(email=admin_email).first()
            admin.phone_verified = True
            admin.email_verified = True
            admin.license_number = 'TN-01-2020-0077881'
            admin.license_verified = True
            admin.license_verification_status = 'approved'
            admin.rating = 5.0
            db.session.commit()
            print(f"[OK] Admin user created: {admin_email} / Admin@7781")
        else:
            # Ensure password is up to date
            admin.password_hash = AuthService.hash_password('Admin@7781')
            admin.license_verified = True
            admin.license_verification_status = 'approved'
            db.session.commit()
            print(f"[OK] Admin user verified: {admin_email}")
            
        print("\n" + "=" * 60)
        print("🎉 ADMIN INITIALIZED SUCCESSFULLY (DATABASE IS CLEAN WITH ZERO HARDCODED RIDES)")
        print("=" * 60)

if __name__ == '__main__':
    seed_database()
