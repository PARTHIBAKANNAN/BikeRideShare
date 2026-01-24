#!/usr/bin/env python3
"""
Test AI-powered ride search using the actual API endpoint
"""

from models.models import db, Ride, User, Bike
from app import create_app
from services.ride_service import RideService

def test_ai_powered_search():
    app = create_app('development')
    with app.app_context():
        print("🚀 Testing AI-Powered Ride Search API")
        print("=" * 50)
        
        # Check available rides
        all_rides = Ride.query.filter_by(status='active').all()
        print(f"📊 Available rides in database: {len(all_rides)}")
        
        for ride in all_rides:
            print(f"   - {ride.from_location} → {ride.to_location} ({ride.departure_date})")
        
        print("\n" + "=" * 50)
        
        # Test Case 1: Direct route search
        print("🧪 TEST 1: Direct route search (Anna Nagar → Tambaram)")
        search_data = {
            'from_location': 'Anna Nagar',
            'to_location': 'Tambaram',
            'travel_date': '2025-08-06',
            'seats_needed': 1
        }
        
        result = RideService.search_rides(search_data, user_id=2)
        print(f"   Result: {result.get('success')}")
        print(f"   AI Powered: {result.get('ai_powered')}")
        print(f"   Search Type: {result.get('search_type')}")
        print(f"   Total Rides: {result.get('total_rides')}")
        print(f"   Message: {result.get('message')}")
        
        if result.get('rides'):
            for i, ride in enumerate(result.get('rides', [])[:2]):
                route = ride.get('route', {})
                score = ride.get('ai_match_score', 0)
                reasoning = ride.get('ai_reasoning', '')
                pickup = ride.get('ai_pickup_suggestion', '')
                
                print(f"\n   🎯 Match {i+1}: {route.get('from_location')} → {route.get('to_location')}")
                print(f"      Score: {score}% | Type: {ride.get('ai_match_type')}")
                if reasoning:
                    print(f"      💡 AI: {reasoning}")
                if pickup:
                    print(f"      📍 Pickup: {pickup}")
        
        print("\n" + "=" * 50)
        
        # Test Case 2: Cross-city intelligent search
        print("🧪 TEST 2: Cross-city intelligent search (Porur → OMR)")
        search_data2 = {
            'from_location': 'Porur',
            'to_location': 'OMR',
            'travel_date': '2025-08-05',
            'seats_needed': 1
        }
        
        result2 = RideService.search_rides(search_data2, user_id=2)
        print(f"   Result: {result2.get('success')}")
        print(f"   AI Powered: {result2.get('ai_powered')}")
        print(f"   Search Type: {result2.get('search_type')}")
        print(f"   Total Rides: {result2.get('total_rides')}")
        print(f"   Message: {result2.get('message')}")
        
        if result2.get('rides'):
            for i, ride in enumerate(result2.get('rides', [])[:2]):
                route = ride.get('route', {})
                score = ride.get('ai_match_score', 0)
                reasoning = ride.get('ai_reasoning', '')
                pickup = ride.get('ai_pickup_suggestion', '')
                
                print(f"\n   🎯 Match {i+1}: {route.get('from_location')} → {route.get('to_location')}")
                print(f"      Score: {score}% | Type: {ride.get('ai_match_type')}")
                if reasoning:
                    print(f"      💡 AI: {reasoning}")
                if pickup:
                    print(f"      📍 Pickup: {pickup}")
        
        print("\n" + "🎉" * 25)
        print("AI-Powered Route Matching Test Complete!")

if __name__ == "__main__":
    test_ai_powered_search() 