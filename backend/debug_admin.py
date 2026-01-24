#!/usr/bin/env python3
"""
Debug admin access issue
"""

import requests
import json

def debug_admin():
    # Login as admin
    login_data = {
        'phone_or_email': 'parthi@admin.com', 
        'password': '7781'
    }
    
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    
    if response.status_code == 200:
        login_result = response.json()
        token = login_result['token']
        user = login_result['user']
        
        print(f"Admin Login Success:")
        print(f"  ID: {user['id']}")
        print(f"  Name: {user['name']}")
        print(f"  Email: {user['email']}")
        print(f"  Phone: {user['phone']}")
        
        # Test admin access
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://localhost:5000/api/admin/check-access', headers=headers)
        
        print(f"\nAdmin Access Check:")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        # Test with direct verification
        from app import create_app
        from services.admin_service import AdminService
        
        app = create_app('default')
        with app.app_context():
            is_admin = AdminService.verify_admin_access(user['id'])
            print(f"\nDirect Admin Check:")
            print(f"  User ID {user['id']} is admin: {is_admin}")
            
    else:
        print(f"Login failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    debug_admin() 