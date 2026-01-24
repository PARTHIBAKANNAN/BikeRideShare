#!/usr/bin/env python3
"""
Test notification system and provider workflow
"""

import requests

def test_provider_notifications():
    print("🧪 Testing Provider Notification System")
    print("=" * 50)
    
    # Login as provider
    login_data = {
        'phone_or_email': 'parthisivaram45@gmail.com', 
        'password': 'Thalamsd@7781'
    }
    
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
    
    if response.status_code == 200:
        token = response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        print('✅ Provider login successful')
        
        # Check notifications
        print("\n📧 Checking Notifications...")
        notifications_response = requests.get('http://localhost:5000/api/notifications', headers=headers)
        print(f'Status: {notifications_response.status_code}')
        
        if notifications_response.status_code == 200:
            notifications_data = notifications_response.json()
            print(f'Total notifications: {notifications_data.get("unread_count", 0)}')
            
            for i, notif in enumerate(notifications_data.get('notifications', [])[:3], 1):
                print(f'  {i}. {notif.get("title")}')
                print(f'     {notif.get("message")}')
                print(f'     Type: {notif.get("type")} | Read: {notif.get("is_read")}')
                print()
        
        # Check pending ride requests
        print("📋 Checking Pending Ride Requests...")
        requests_response = requests.get('http://localhost:5000/api/ride-requests/pending', headers=headers)
        print(f'Status: {requests_response.status_code}')
        
        if requests_response.status_code == 200:
            pending_data = requests_response.json()
            print(f'Pending requests: {pending_data.get("count", 0)}')
            
            for i, req in enumerate(pending_data.get('pending_requests', [])[:3], 1):
                print(f'  {i}. {req.get("passenger_name")} wants to join ride {req.get("ride_id")}')
                print(f'     Pickup: {req.get("pickup_location")}')
                print(f'     Message: {req.get("message")}')
                print(f'     Phone: {req.get("passenger_phone")}')
                print()
                
                # Test accept workflow
                if i == 1:  # Accept the first request
                    print(f'🎯 Testing Accept Request {req.get("id")}...')
                    accept_response = requests.post(
                        'http://localhost:5000/api/ride-requests/accept',
                        json={'ride_request_id': req.get('id')},
                        headers=headers
                    )
                    print(f'Accept Status: {accept_response.status_code}')
                    if accept_response.status_code == 200:
                        result = accept_response.json()
                        print('✅ Request accepted!')
                        contact = result.get('contact_info', {})
                        print(f'📞 Contact Exchange:')
                        print(f'   Passenger: {contact.get("passenger_name")} - {contact.get("passenger_phone")}')
                        print(f'   Provider: {contact.get("provider_name")} - {contact.get("provider_phone")}')
                    else:
                        print(f'❌ Accept failed: {accept_response.text}')
        
        print("\n🎉 Provider workflow test complete!")
        
    else:
        print('❌ Login failed')

if __name__ == "__main__":
    test_provider_notifications() 