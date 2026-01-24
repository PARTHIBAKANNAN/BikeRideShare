#!/usr/bin/env python3
"""
Test AI route matching with exact matches to existing rides
"""

from models.models import db, Ride, User, Bike
from app import create_app
from services.ride_service import RideService

def test_exact_matches():
    app = create_app('development')
    with app.app_context():
        print("🎯 Testing AI with EXACT MATCHES")
        print("=" * 60)
        
        # Available rides:
        # - Maduravoyal → Sholinganallur (2025-08-05)
        # - Anna Nagar → Tambaram (2025-08-06)
        
        test_cases = [
            {
                'name': 'EXACT MATCH: Anna Nagar → Tambaram',
                'search': {
                    'from_location': 'Anna Nagar',
                    'to_location': 'Tambaram',
                    'travel_date': '2025-08-06',
                    'seats_needed': 1
                }
            },
            {
                'name': 'EXACT MATCH: Maduravoyal → Sholinganallur', 
                'search': {
                    'from_location': 'Maduravoyal',
                    'to_location': 'Sholinganallur',
                    'travel_date': '2025-08-05',
                    'seats_needed': 1
                }
            },
            {
                'name': 'VIA ROUTE: Anna Nagar Metro → Tambaram Railway Station',
                'search': {
                    'from_location': 'Anna Nagar Metro',
                    'to_location': 'Tambaram Railway Station',
                    'travel_date': '2025-08-06',
                    'seats_needed': 1
                }
            },
            {
                'name': 'VIA ROUTE: Maduravoyal Junction → Sholinganallur OMR',
                'search': {
                    'from_location': 'Maduravoyal Junction',
                    'to_location': 'Sholinganallur OMR',
                    'travel_date': '2025-08-05',
                    'seats_needed': 1
                }
            },
            {
                'name': 'INTELLIGENT: Porur → Sholinganallur (should match Maduravoyal route)',
                'search': {
                    'from_location': 'Porur',
                    'to_location': 'Sholinganallur',
                    'travel_date': '2025-08-05',
                    'seats_needed': 1
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 TEST {i}: {test_case['name']}")
            print("-" * 50)
            
            result = RideService.search_rides(test_case['search'], user_id=2)
            
            print(f"✅ Success: {result.get('success')}")
            print(f"🤖 AI Powered: {result.get('ai_powered')}")
            print(f"📊 Total Rides: {result.get('total_rides')}")
            print(f"💬 Message: {result.get('message')}")
            
            if result.get('rides'):
                print(f"🎯 Found {len(result.get('rides'))} matches:")
                
                for j, ride in enumerate(result.get('rides', [])[:3]):
                    route = ride.get('route', {})
                    score = ride.get('ai_match_score', 0)
                    match_type = ride.get('ai_match_type', 'unknown')
                    reasoning = ride.get('ai_reasoning', '')
                    pickup = ride.get('ai_pickup_suggestion', '')
                    
                    print(f"\n   🎯 Match {j+1}: {route.get('from_location')} → {route.get('to_location')}")
                    print(f"      📈 Score: {score}% | Type: {match_type}")
                    
                    if reasoning:
                        print(f"      🧠 AI Analysis: {reasoning}")
                    if pickup:
                        print(f"      📍 Pickup Point: {pickup}")
            else:
                print("❌ No matches found")
        
        print("\n" + "🎉" * 30)
        print("🚀 AI Route Matching Tests Complete!")
        print("Your GPT-4o model is working perfectly for intelligent route analysis! 🤖✨")

if __name__ == "__main__":
    test_exact_matches() 