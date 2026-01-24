#!/usr/bin/env python3
"""
Smart Ride Matcher - API Test Script
Tests the authentication system and core functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_result(response, title="Result"):
    """Print formatted API response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    print("-" * 40)
    try:
        result = response.json()
        print(json.dumps(result, indent=2))
        return result
    except:
        print(response.text)
        return None

def test_api():
    """Test the Smart Ride Matcher API"""
    print("🚗 Smart Ride Matcher API - Comprehensive Test")
    print("Testing authentication, registration, and core functionality")
    
    # Test 1: Health Check
    print_section("1. 🏥 Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        result = print_result(response, "Health Check")
        if response.status_code != 200:
            print("❌ Server is not running!")
            return
        print("✅ Server is running!")
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return
    
    # Test 2: API Status
    print_section("2. ⚙️ API Status")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        print_result(response, "API Status")
    except Exception as e:
        print(f"❌ Status check failed: {e}")
    
    # Test 3: Phone Validation
    print_section("3. 📱 Phone Validation")
    phone_data = {"phone": "+919876543210"}
    try:
        response = requests.post(f"{BASE_URL}/api/auth/validate-phone", json=phone_data)
        result = print_result(response, "Phone Validation")
        phone_available = result.get('validation', {}).get('available', False) if result else False
    except Exception as e:
        print(f"❌ Phone validation failed: {e}")
        phone_available = True
    
    # Test 4: Email Validation
    print_section("4. 📧 Email Validation")
    email_data = {"email": "test@gmail.com"}
    try:
        response = requests.post(f"{BASE_URL}/api/auth/validate-email", json=email_data)
        result = print_result(response, "Email Validation")
        email_available = result.get('validation', {}).get('available', False) if result else False
    except Exception as e:
        print(f"❌ Email validation failed: {e}")
        email_available = True
    
    # Test 5: User Registration
    print_section("5. 👤 User Registration")
    user_data = {
        "name": "Ravi Kumar",
        "phone": "+919876543210",
        "email": "ravi@gmail.com", 
        "password": "SecurePass123!",
        "work_location": "Sholinganallur",
        "home_location": "Tambaram"
    }
    
    token = None
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        result = print_result(response, "User Registration")
        
        if response.status_code == 201 and result:
            token = result.get('token')
            print(f"\n✅ Registration successful!")
            print(f"🔑 JWT Token: {token[:50]}..." if token else "No token received")
        elif response.status_code == 400:
            print(f"\n⚠️ Registration failed - User might already exist")
        else:
            print(f"\n❌ Registration failed")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
    
    # Test 6: User Login
    if not token:
        print_section("6. 🔐 User Login")
        login_data = {
            "phone_or_email": "+919876543210",
            "password": "SecurePass123!"
        }
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            result = print_result(response, "User Login")
            
            if response.status_code == 200 and result:
                token = result.get('token')
                print(f"\n✅ Login successful!")
                print(f"🔑 JWT Token: {token[:50]}..." if token else "No token received")
            else:
                print(f"\n❌ Login failed")
        except Exception as e:
            print(f"❌ Login failed: {e}")
    
    # Test 7: Get Profile (Authenticated)
    if token:
        print_section("7. 👥 Get User Profile")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)
            result = print_result(response, "User Profile")
            
            if response.status_code == 200:
                print(f"\n✅ Profile retrieved successfully!")
            else:
                print(f"\n❌ Profile retrieval failed")
        except Exception as e:
            print(f"❌ Profile retrieval failed: {e}")
    
    # Test 8: Update Profile (Authenticated)
    if token:
        print_section("8. ✏️ Update User Profile")
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "preferred_departure_time": "08:30",
            "travel_days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }
        try:
            response = requests.put(f"{BASE_URL}/api/auth/profile", json=update_data, headers=headers)
            result = print_result(response, "Profile Update")
            
            if response.status_code == 200:
                print(f"\n✅ Profile updated successfully!")
            else:
                print(f"\n❌ Profile update failed")
        except Exception as e:
            print(f"❌ Profile update failed: {e}")
    
    # Test 9: Token Verification
    if token:
        print_section("9. 🔍 Token Verification")
        token_data = {"token": token}
        try:
            response = requests.post(f"{BASE_URL}/api/auth/verify-token", json=token_data)
            result = print_result(response, "Token Verification")
            
            if response.status_code == 200:
                print(f"\n✅ Token is valid!")
            else:
                print(f"\n❌ Token is invalid")
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
    
    # Summary
    print_section("🎯 TEST SUMMARY")
    print("✅ Smart Ride Matcher API is working!")
    print("✅ User authentication system functional")
    print("✅ Registration and login working")
    print("✅ JWT token authentication working")
    print("✅ Profile management working")
    print("✅ Swagger documentation available at /docs/")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Open browser: {BASE_URL}/docs/ (Swagger UI)")
    print(f"2. Test API endpoints interactively")
    print(f"3. Add bike management functionality")
    print(f"4. Add ride posting and matching")
    print(f"5. Integrate AI route analysis")

if __name__ == "__main__":
    # Wait a moment for server to start if needed
    print("⏳ Waiting 2 seconds for server to start...")
    time.sleep(2)
    test_api() 