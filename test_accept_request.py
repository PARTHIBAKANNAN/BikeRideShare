#!/usr/bin/env python3
"""
Test accepting Request 2 (from different user)
"""

import requests

def test_accept_request():
    print("🧪 Testing Accept Request (Non-Self Request)")
    print("=" * 50)
    
    # Login as provider
    login_data = {'phone_or_email': 'parthisivaram45@gmail.com', 'password': 'Thalamsd@7781'}
    response = requests.post('http://localhost:5000/api/auth/login', json=login_data)

    if response.status_code == 200:
        token = response.json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        print('✅ Provider login successful')
        
        # Get pending requests
        req_response = requests.get('http://localhost:5000/api/ride-requests/pending', headers=headers)
        if req_response.status_code == 200:
            data = req_response.json()
            requests_list = data.get('pending_requests', [])
            print(f'📋 Found {len(requests_list)} pending requests')
            
            # Find a request from a different user (not self-request)
            valid_request = None
            for req in requests_list:
                passenger_id = req.get('passenger_id')
                if passenger_id != 2:  # Not from current user (ID: 2)
                    valid_request = req
                    break
            
            if valid_request:
                req_id = valid_request['id']
                passenger_name = valid_request.get('passenger_name', 'Unknown')
                passenger_id = valid_request.get('passenger_id')
                
                print(f'🎯 Testing accept for Request {req_id}')
                print(f'   From: {passenger_name} (ID: {passenger_id})')
                print(f'   Message: {valid_request.get("message", "No message")}')
                
                accept_data = {'ride_request_id': req_id}
                accept_resp = requests.post('http://localhost:5000/api/ride-requests/accept', 
                                          json=accept_data, headers=headers)
                
                print(f'\nAccept status: {accept_resp.status_code}')
                
                if accept_resp.status_code == 200:
                    result = accept_resp.json()
                    print('🎉 SUCCESS! Request accepted!')
                    
                    contact = result.get('contact_info', {})
                    if contact:
                        print(f'\n📞 Contact Exchange:')
                        print(f'   Passenger: {contact.get("passenger_name")} - {contact.get("passenger_phone")}')
                        print(f'   Provider: {contact.get("provider_name")} - {contact.get("provider_phone")}')
                else:
                    print(f'❌ Failed: {accept_resp.text}')
                    
                    # Add more debugging
                    print(f'\n🔍 Debug Info:')
                    print(f'   Request ID: {req_id}')
                    print(f'   Request ride_id: {valid_request.get("ride_id")}')
                    print(f'   Passenger ID: {passenger_id}')
                    print(f'   Current user (provider): 2')
            else:
                print('❌ No valid non-self requests found to test')
                print('All requests are self-requests (user trying to join own ride)')
        else:
            print(f'❌ Failed to get pending requests: {req_response.text}')
    else:
        print('❌ Login failed')

if __name__ == "__main__":
    test_accept_request() 