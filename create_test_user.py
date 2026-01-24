#!/usr/bin/env python3
"""
Create a test user for testing ride joining functionality
"""

import requests
import json

def create_test_user():
    print("🧪 Creating Test User for Ride Testing")
    print("=" * 50)
    
    # Register new test user
    user_data = {
        'name': 'Test Passenger',
        'email': 'testpassenger@gmail.com',
        'phone': '+919988776655',
        'password': 'TestPass@123',
        'confirm_password': 'TestPass@123',
        'home_location': 'Nungambakkam',
        'work_location': 'Anna Nagar'
    }
    
    print("📝 Registering test user...")
    response = requests.post('http://localhost:5000/api/auth/register', json=user_data)
    
    if response.status_code == 201:
        print("✅ Test user registered successfully!")
        user_info = response.json()
        
        # Login as test user
        login_data = {
            'phone_or_email': 'testpassenger@gmail.com',
            'password': 'TestPass@123'
        }
        
        print("\n🔐 Logging in as test user...")
        login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['token']
            headers = {'Authorization': f'Bearer {token}'}
            print("✅ Test user login successful!")
            
            # Search for available rides
            print("\n🔍 Searching for rides to join...")
            search_data = {
                'from_location': 'Kilpauk',
                'to_location': 'Koyambedu'
            }
            
            search_response = requests.post('http://localhost:5000/api/rides/search', 
                                          json=search_data, headers=headers)
            
            if search_response.status_code == 200:
                rides_data = search_response.json()
                rides = rides_data.get('rides', [])
                print(f"📍 Found {len(rides)} available rides")
                
                if rides:
                    # Try to join the first ride
                    first_ride = rides[0]
                    ride_id = first_ride['id']
                    provider_name = first_ride.get('rider', {}).get('name', 'Unknown')
                    
                    print(f"\n🎯 Attempting to join ride {ride_id} by {provider_name}...")
                    
                    join_data = {
                        'message': 'Hi! I would like to join this ride as a test passenger.',
                        'pickup_location': 'Kilpauk Metro Station'
                    }
                    
                    join_response = requests.post(f'http://localhost:5000/api/rides/{ride_id}/join',
                                                json=join_data, headers=headers)
                    
                    print(f"Join Status: {join_response.status_code}")
                    if join_response.status_code == 201:
                        print("🎉 Successfully joined ride!")
                        print("📧 Provider should now have a notification!")
                        
                        # Show what the provider will see
                        print("\n" + "="*50)
                        print("👤 PROVIDER DASHBOARD PREVIEW:")
                        print("="*50)
                        print(f"📧 New notification: 'Test Passenger wants to join your ride'")
                        print(f"📱 Phone: +919988776655")
                        print(f"📍 Pickup: Kilpauk Metro Station")
                        print(f"💬 Message: 'Hi! I would like to join this ride as a test passenger.'")
                        print("\n🎯 Now you can:")
                        print("  1. Login as provider (parthisivaram45@gmail.com)")
                        print("  2. Go to Notifications page")
                        print("  3. Accept/Reject the ride request")
                        print("  4. See contact exchange on acceptance!")
                    else:
                        print(f"❌ Failed to join ride: {join_response.text}")
                else:
                    print("❌ No rides available to join")
            else:
                print(f"❌ Search failed: {search_response.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
    
    elif response.status_code == 400 and 'already exists' in response.text:
        print("ℹ️  Test user already exists!")
        
        # Just try to login and join ride
        login_data = {
            'phone_or_email': 'testpassenger@gmail.com',
            'password': 'TestPass@123'
        }
        
        print("🔐 Logging in as existing test user...")
        login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['token']
            headers = {'Authorization': f'Bearer {token}'}
            print("✅ Test user login successful!")
            
            # Search and join ride (same logic as above)
            search_data = {'from_location': 'Kilpauk', 'to_location': 'Koyambedu'}
            search_response = requests.post('http://localhost:5000/api/rides/search', 
                                          json=search_data, headers=headers)
            
            if search_response.status_code == 200:
                rides = search_response.json().get('rides', [])
                if rides:
                    ride_id = rides[0]['id']
                    join_data = {
                        'message': 'Test join request from existing user!',
                        'pickup_location': 'Kilpauk Metro Station'
                    }
                    
                    join_response = requests.post(f'http://localhost:5000/api/rides/{ride_id}/join',
                                                json=join_data, headers=headers)
                    
                    if join_response.status_code == 201:
                        print("🎉 Successfully created another join request!")
                    else:
                        print(f"Join status: {join_response.status_code} - {join_response.text}")
        
    else:
        print(f"❌ Registration failed: {response.text}")

if __name__ == "__main__":
    create_test_user() 