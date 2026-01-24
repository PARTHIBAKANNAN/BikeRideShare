#!/usr/bin/env python3
"""
Test Azure OpenAI integration and AI route matching with real database rides
"""

from models.models import db, Ride, User, Bike
from app import create_app
from services.ai_route_matcher import ai_route_matcher

def test_ai_integration():
    app = create_app('development')
    with app.app_context():
        print('🔧 Testing Azure OpenAI Configuration...')
        print(f'   AI Configured: {ai_route_matcher.is_configured}')
        
        if ai_route_matcher.is_configured:
            print('   ✅ Azure OpenAI is properly configured')
            print(f'   🤖 Model: {ai_route_matcher.deployment_name}')
        else:
            print('   ❌ Azure OpenAI configuration failed')
        
        # Get real rides from database
        real_rides = Ride.query.filter_by(status='active').all()
        print(f'\n📊 Real rides in database: {len(real_rides)}')
        
        for ride in real_rides:
            print(f'   - {ride.from_location} → {ride.to_location} ({ride.departure_date})')
        
        if len(real_rides) > 0:
            # Test AI search with real data
            search_request = {
                'from_location': 'Anna Nagar',
                'to_location': 'Tambaram',
                'departure_date': '2025-08-06',
                'seats_needed': 1
            }
            
            # Convert real rides to dict format for AI
            available_rides = []
            for ride in real_rides:
                ride_dict = ride.to_dict()
                available_rides.append(ride_dict)
            
            print('\n🤖 Testing AI route matching...')
            try:
                matched_rides = ai_route_matcher.find_intelligent_matches(search_request, available_rides)
                print(f'   ✅ AI matching successful!')
                print(f'   📈 Matched rides: {len(matched_rides)}')
                
                for i, ride in enumerate(matched_rides[:3]):  # Show top 3 matches
                    score = ride.get('ai_match_score', 0)
                    match_type = ride.get('ai_match_type', 'unknown')
                    reasoning = ride.get('ai_reasoning', '')
                    pickup = ride.get('ai_pickup_suggestion', '')
                    
                    print(f'\n   🎯 Match {i+1}: {ride.get("from_location")} → {ride.get("to_location")}')
                    print(f'      Score: {score}% | Type: {match_type}')
                    if reasoning:
                        print(f'      💡 Reasoning: {reasoning}')
                    if pickup:
                        print(f'      📍 Pickup: {pickup}')
                        
            except Exception as e:
                print(f'   ❌ AI matching failed: {e}')
                import traceback
                traceback.print_exc()
        else:
            print('❌ No rides found in database to test with')

if __name__ == "__main__":
    test_ai_integration() 