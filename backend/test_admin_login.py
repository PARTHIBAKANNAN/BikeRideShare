#!/usr/bin/env python3
"""
Test admin login functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

def test_admin_login():
    """Test admin login with hardcoded credentials"""
    print("🔐 Testing admin login...")
    
    # Admin credentials
    admin_data = {
        "phone_or_email": "parthi@admin.com",
        "password": "7781"
    }
    
    # Test login
    response = requests.post(f"{API_URL}/auth/login", json=admin_data)
    
    if response.status_code == 200:
        print("✅ Admin login successful!")
        
        login_response = response.json()
        token = login_response.get('token')
        user = login_response.get('user', {})
        
        print(f"   Admin Name: {user.get('name')}")
        print(f"   Admin Email: {user.get('email')}")
        print(f"   Token received: {'Yes' if token else 'No'}")
        
        if token:
            # Test admin access
            headers = {"Authorization": f"Bearer {token}"}
            
            print("\n🛡️ Testing admin access check...")
            response = requests.get(f"{API_URL}/admin/check-access", headers=headers)
            
            if response.status_code == 200:
                access_response = response.json()
                if access_response.get('has_admin_access'):
                    print("✅ Admin access verified!")
                    
                    # Test admin dashboard
                    print("\n📊 Testing admin dashboard...")
                    response = requests.get(f"{API_URL}/admin/dashboard", headers=headers)
                    
                    if response.status_code == 200:
                        print("✅ Admin dashboard accessible!")
                        dashboard_data = response.json()
                        
                        if 'platform_stats' in dashboard_data:
                            stats = dashboard_data['platform_stats']
                            print(f"   Total Users: {stats.get('total_users', 0)}")
                            print(f"   Total Bikes: {stats.get('total_bikes', 0)}")
                            print(f"   Total Rides: {stats.get('total_rides', 0)}")
                        
                        return True
                    else:
                        print(f"❌ Admin dashboard failed: {response.status_code}")
                        return False
                else:
                    print("❌ Admin access denied!")
                    return False
            else:
                print(f"❌ Admin access check failed: {response.status_code}")
                return False
        else:
            print("❌ No token received!")
            return False
            
    else:
        print(f"❌ Admin login failed: {response.status_code} - {response.text}")
        return False

def test_health_check():
    """Test if backend is running"""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def main():
    """Run admin login test"""
    print("🧪 Testing Admin Login Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Backend not running. Please start the Flask app first.")
        return
    
    # Test 2: Admin login
    success = test_admin_login()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Admin login test completed successfully!")
        print("\n✅ You can now login as admin with:")
        print("   Email: parthi@admin.com")
        print("   Password: 7781")
    else:
        print("❌ Admin login test failed!")

if __name__ == "__main__":
    main() 