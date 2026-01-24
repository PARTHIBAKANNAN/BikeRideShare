#!/usr/bin/env python3
"""
Create admin user for the system
"""

from app import create_app
from models.models import db, User
from services.auth_service import AuthService

def create_admin_user():
    """Create the admin user"""
    app = create_app('default')
    with app.app_context():
        # Admin credentials
        admin_email = "parthi@admin.com"
        admin_password = "Admin123!"  # Strong password
        admin_phone = "+919876543213"  # Unique phone number
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"✅ Admin user already exists: {admin_email}")
            return existing_admin
        
        # Create admin user
        try:
            admin_data = {
                'name': 'Admin Parthi',
                'phone': admin_phone,
                'email': admin_email,
                'password': admin_password,
                'work_location': 'T. Nagar',
                'home_location': 'Anna Nagar'
            }
            
            result = AuthService.register_user(admin_data)
            
            if result['success']:
                # Mark as verified
                admin_user = User.query.filter_by(email=admin_email).first()
                admin_user.phone_verified = True
                admin_user.email_verified = True
                admin_user.is_active = True
                
                db.session.commit()
                
                print(f"✅ Admin user created successfully: {admin_email}")
                print(f"   Password: {admin_password}")
                print(f"   Phone: {admin_phone}")
                return admin_user
            else:
                print(f"❌ Failed to create admin user: {result.get('errors')}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            return None

if __name__ == "__main__":
    print("🔧 Creating admin user...")
    create_admin_user() 