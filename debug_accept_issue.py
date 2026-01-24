#!/usr/bin/env python3
"""
Debug script to analyze ride request and ownership issue
"""

import requests
import json

def debug_accept_issue():
    print("🔍 Debugging Accept Ride Request Issue")
    print("=" * 50)
    
    # Login as provider
    login_data = {'phone_or_email': 'parthisivaram45@gmail.com', 'password': 'Thalamsd@7781'}
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data)

    if response.status_code == 200:
        token = response.json()['token']
        user_data = response.json()['user']
        headers = {'Authorization': f'Bearer {token}'}
        current_user_id = user_data['id']
        
        print(f'✅ Login successful')
        print(f'Current User ID: {current_user_id} ({user_data["name"]})')
        
        # Get pending requests
        req_response = requests.get('http://localhost:5000/api/ride-requests/pending', headers=headers)
        if req_response.status_code == 200:
            data = req_response.json()
            requests_list = data.get('pending_requests', [])
            print(f'\n📋 Found {len(requests_list)} pending requests')
            
            if requests_list:
                for i, req in enumerate(requests_list[:2], 1):
                    print(f'\n--- Request {i} ---')
                    print(f'Request ID: {req.get("id")}')
                    print(f'Ride ID: {req.get("ride_id")}')
                    print(f'Passenger: {req.get("passenger_name")} (ID: {req.get("passenger_id")})')
                    print(f'Message: {req.get("message")}')
        
        # Get my rides to check ownership
        rides_response = requests.get('http://localhost:5000/api/rides/my-rides?type=all', headers=headers)
        if rides_response.status_code == 200:
            rides_data = rides_response.json()
            rides = rides_data.get('rides', [])
            print(f'\n🚗 My Rides ({len(rides)}):')
            
            for ride in rides:
                ride_id = ride.get('id')
                rider_id = ride.get('rider_id')
                user_id = ride.get('user_id')
                route_from = ride.get('route', {}).get('from_location', 'Unknown')
                route_to = ride.get('route', {}).get('to_location', 'Unknown')
                
                print(f'  Ride {ride_id}: {route_from} → {route_to}')
                print(f'    rider_id: {rider_id}, user_id: {user_id}')
                print(f'    Ownership check: rider_id == current_user_id? {rider_id == current_user_id}')
        
        # Now check which requests match which rides
        print(f'\n🔗 Request-Ride Matching:')
        if requests_list and rides:
            for req in requests_list[:2]:
                req_ride_id = req.get('ride_id')
                matching_ride = next((r for r in rides if r.get('id') == req_ride_id), None)
                
                if matching_ride:
                    print(f'  Request {req.get("id")} → Ride {req_ride_id}: ✅ MATCH')
                    print(f'    Ride owner: {matching_ride.get("rider_id")}')
                    print(f'    Current user: {current_user_id}')
                    print(f'    Can accept: {matching_ride.get("rider_id") == current_user_id}')
                else:
                    print(f'  Request {req.get("id")} → Ride {req_ride_id}: ❌ NO MATCHING RIDE FOUND')
        
        print(f'\n🎯 Analysis Complete!')
    else:
        print('❌ Login failed')

if __name__ == "__main__":
    debug_accept_issue() 