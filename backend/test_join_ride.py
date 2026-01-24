#!/usr/bin/env python3
"""
Test ride join functionality to debug 400 error
"""

import requests

def test_join_ride():
    print("🧪 Testing Ride Join Functionality")
    print("=" * 40)
    
    # Login first
    login_data = {
        'phone_or_email': 'parthisivaram45@gmail.com', 
        'password': 'Thalamsd@7781'
    }
    
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    
    if response.status_code == 200:
        token = response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        print('✅ Login successful')
        
        # Test join ride with detailed error
        join_data = {
            'message': 'I want to join this ride',
            'pickup_location': 'Maduravoyal Junction'
        }
        
        print(f"📤 Sending join request: {join_data}")
        response = requests.post('http://localhost:5000/api/rides/1/join', json=join_data, headers=headers)
        
        print(f"📥 Join Status: {response.status_code}")
        print(f"📥 Join Response: {response.text}")
        
        if response.status_code == 400:
            print('❌ 400 Error Details:')
            try:
                error_data = response.json()
                print(f'   Error: {error_data.get("error", "Unknown error")}')
                print(f'   Details: {error_data}')
            except Exception as e:
                print(f'   Raw response: {response.text}')
                print(f'   Parse error: {e}')
        elif response.status_code == 201:
            print('✅ Join successful!')
            result = response.json()
            print(f'   Message: {result.get("message")}')
    else:
        print(f'❌ Login failed: {response.status_code}')
        print(f'   Response: {response.text}')

if __name__ == "__main__":
    test_join_ride() 