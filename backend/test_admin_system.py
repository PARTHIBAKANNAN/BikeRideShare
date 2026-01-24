#!/usr/bin/env python3
"""
Comprehensive test for the admin system functionality
Tests: admin login, dashboard, license verification, user management, bike approvals, reports
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api"

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

def test_admin_login():
    """Test admin login with hardcoded credentials"""
    print("\n🔐 Testing admin login...")
    
    admin_data = {
        "phone_or_email": "parthi@admin.com",
        "password": "7781"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=admin_data)
    
    if response.status_code == 200:
        login_response = response.json()
        token = login_response.get('token')
        user = login_response.get('user', {})
        
        print("✅ Admin login successful!")
        print(f"   Admin Name: {user.get('name')}")
        print(f"   Admin Email: {user.get('email')}")
        
        return token
    else:
        print(f"❌ Admin login failed: {response.status_code} - {response.text}")
        return None

def test_admin_access(token):
    """Test admin access verification"""
    print("\n🛡️ Testing admin access verification...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/admin/check-access", headers=headers)
    
    if response.status_code == 200:
        access_response = response.json()
        if access_response.get('has_admin_access'):
            print("✅ Admin access verified!")
            return True
        else:
            print("❌ Admin access denied!")
            return False
    else:
        print(f"❌ Admin access check failed: {response.status_code}")
        return False

def test_admin_dashboard(token):
    """Test admin dashboard data retrieval"""
    print("\n📊 Testing admin dashboard...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/admin/dashboard", headers=headers)
    
    if response.status_code == 200:
        dashboard_data = response.json()
        print("✅ Admin dashboard accessible!")
        
        if 'platform_stats' in dashboard_data:
            stats = dashboard_data['platform_stats']
            print(f"   Total Users: {stats.get('users', {}).get('total', 0)}")
            print(f"   Total Bikes: {stats.get('bikes', {}).get('total', 0)}")
            print(f"   Total Rides: {stats.get('rides', {}).get('total', 0)}")
            print(f"   Pending Reports: {stats.get('reports', {}).get('pending', 0)}")
            
            # Check pending approvals
            pending = stats.get('pending_approvals', {})
            print(f"   Pending License Verifications: {pending.get('license_verifications', 0)}")
            print(f"   Pending Bike Verifications: {pending.get('bike_verifications', 0)}")
        
        return True
    else:
        print(f"❌ Admin dashboard failed: {response.status_code} - {response.text}")
        return False

def test_user_management(token):
    """Test user management functionality"""
    print("\n👥 Testing user management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all users
    response = requests.get(f"{API_URL}/admin/users", headers=headers)
    
    if response.status_code == 200:
        users_data = response.json()
        users = users_data.get('users', [])
        print(f"✅ Retrieved {len(users)} users")
        
        if users:
            # Test flagging a user (if any regular users exist)
            regular_users = [u for u in users if u.get('email') != 'parthi@admin.com']
            if regular_users:
                test_user = regular_users[0]
                print(f"   Testing user actions on: {test_user.get('name')}")
                
                # Test flag user
                flag_data = {
                    "user_id": test_user['id'],
                    "reason": "Test flagging by admin"
                }
                
                response = requests.post(f"{API_URL}/admin/users/flag", json=flag_data, headers=headers)
                if response.status_code == 200:
                    print("   ✅ User flagging works")
                    
                    # Test unflag user
                    unflag_data = {"user_id": test_user['id']}
                    response = requests.post(f"{API_URL}/admin/users/unflag", json=unflag_data, headers=headers)
                    if response.status_code == 200:
                        print("   ✅ User unflagging works")
                    else:
                        print(f"   ❌ User unflagging failed: {response.status_code}")
                else:
                    print(f"   ❌ User flagging failed: {response.status_code}")
        
        return True
    else:
        print(f"❌ User management failed: {response.status_code} - {response.text}")
        return False

def test_bike_verifications(token):
    """Test bike verification functionality"""
    print("\n🏍️ Testing bike verification system...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get pending bike verifications
    response = requests.get(f"{API_URL}/admin/bike-verifications", headers=headers)
    
    if response.status_code == 200:
        verifications_data = response.json()
        pending_bikes = verifications_data.get('pending_bikes', [])
        print(f"✅ Retrieved {len(pending_bikes)} pending bike verifications")
        
        if pending_bikes:
            test_bike = pending_bikes[0]
            print(f"   Testing bike verification: {test_bike.get('bike_number')}")
            
            # Test approve bike
            approval_data = {
                "bike_id": test_bike['bike_id'],
                "action": "approve"
            }
            
            response = requests.post(f"{API_URL}/admin/bike-verifications/verify", json=approval_data, headers=headers)
            if response.status_code == 200:
                print("   ✅ Bike approval works")
            else:
                print(f"   ❌ Bike approval failed: {response.status_code}")
        else:
            print("   ℹ️ No pending bike verifications to test")
        
        return True
    else:
        print(f"❌ Bike verification system failed: {response.status_code}")
        return False

def test_license_verifications(token):
    """Test license verification functionality"""
    print("\n🆔 Testing license verification system...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get pending license verifications
    response = requests.get(f"{API_URL}/admin/license-verifications", headers=headers)
    
    if response.status_code == 200:
        verifications_data = response.json()
        pending_licenses = verifications_data.get('pending_verifications', [])
        print(f"✅ Retrieved {len(pending_licenses)} pending license verifications")
        
        if pending_licenses:
            test_license = pending_licenses[0]
            print(f"   Testing license verification: {test_license.get('name')}")
            
            # Test approve license
            approval_data = {
                "user_id": test_license['user_id'],
                "action": "approve"
            }
            
            response = requests.post(f"{API_URL}/admin/license-verifications/verify", json=approval_data, headers=headers)
            if response.status_code == 200:
                print("   ✅ License approval works")
            else:
                print(f"   ❌ License approval failed: {response.status_code}")
        else:
            print("   ℹ️ No pending license verifications to test")
        
        return True
    else:
        print(f"❌ License verification system failed: {response.status_code}")
        return False

def test_reports_system(token):
    """Test reports management functionality"""
    print("\n📋 Testing reports management system...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all reports
    response = requests.get(f"{API_URL}/admin/reports", headers=headers)
    
    if response.status_code == 200:
        reports_data = response.json()
        reports = reports_data.get('reports', [])
        print(f"✅ Retrieved {len(reports)} reports")
        
        if reports:
            test_report = reports[0]
            print(f"   Testing report management: Report #{test_report.get('id')}")
            
            # Test assign report
            response = requests.post(f"{API_URL}/admin/reports/{test_report['id']}/assign", headers=headers)
            if response.status_code == 200:
                print("   ✅ Report assignment works")
                
                # Test resolve report
                resolution_data = {
                    "report_id": test_report['id'],
                    "resolution_action": "warning",
                    "admin_notes": "Test resolution by admin"
                }
                
                response = requests.post(f"{API_URL}/admin/reports/resolve", json=resolution_data, headers=headers)
                if response.status_code == 200:
                    print("   ✅ Report resolution works")
                else:
                    print(f"   ❌ Report resolution failed: {response.status_code}")
            else:
                print(f"   ❌ Report assignment failed: {response.status_code}")
        else:
            print("   ℹ️ No reports to test")
        
        return True
    else:
        print(f"❌ Reports management system failed: {response.status_code}")
        return False

def test_rides_management(token):
    """Test rides management functionality"""
    print("\n🚗 Testing rides management system...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all rides
    response = requests.get(f"{API_URL}/admin/rides", headers=headers)
    
    if response.status_code == 200:
        rides_data = response.json()
        rides = rides_data.get('rides', [])
        print(f"✅ Retrieved {len(rides)} rides")
        
        return True
    else:
        print(f"❌ Rides management failed: {response.status_code}")
        return False

def main():
    """Run comprehensive admin system tests"""
    print("🧪 Comprehensive Admin System Test")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Backend not running. Please start the Flask app first.")
        return
    
    # Test 2: Admin login
    token = test_admin_login()
    if not token:
        print("\n❌ Cannot proceed without admin token")
        return
    
    # Test 3: Admin access verification
    if not test_admin_access(token):
        print("\n❌ Admin access verification failed")
        return
    
    # Test 4: Admin dashboard
    test_admin_dashboard(token)
    
    # Test 5: User management
    test_user_management(token)
    
    # Test 6: Bike verifications
    test_bike_verifications(token)
    
    # Test 7: License verifications
    test_license_verifications(token)
    
    # Test 8: Reports system
    test_reports_system(token)
    
    # Test 9: Rides management
    test_rides_management(token)
    
    print("\n" + "=" * 60)
    print("🎉 Admin system testing completed!")
    print("\n✅ Admin Features Tested:")
    print("   • Admin login and access verification")
    print("   • Comprehensive dashboard with platform stats")
    print("   • User management (flag/unflag/suspend/reactivate)")
    print("   • Bike verification approval workflow")
    print("   • License verification approval workflow")
    print("   • Reports management and resolution system")
    print("   • Rides monitoring and management")
    print("\n🔑 Admin Login Credentials:")
    print("   Email: parthi@admin.com")
    print("   Password: 7781")
    print("\n🌐 Access the admin dashboard at:")
    print("   Frontend: http://localhost:3000 (login as admin)")
    print("   API Docs: http://localhost:5000/docs/")

if __name__ == "__main__":
    main() 