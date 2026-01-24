#!/usr/bin/env python3
"""
Debug AI response for exact match
"""

from models.models import db, Ride
from app import create_app
from services.ride_service import RideService

def debug_ai_response():
    app = create_app('development')
    with app.app_context():
        print('🔍 DEBUG: Testing exact match with AI response...')
        
        search_data = {
            'from_location': 'Maduravoyal',
            'to_location': 'Sholinganallur',
            'travel_date': '2025-08-05',
            'seats_needed': 1
        }
        
        result = RideService.search_rides(search_data, user_id=None)  # Don't exclude any rides for testing
        print(f'Success: {result.get("success")}')
        print(f'AI Powered: {result.get("ai_powered")}')
        print(f'Total Rides: {result.get("total_rides")}')
        print(f'Message: {result.get("message")}')

if __name__ == "__main__":
    debug_ai_response() 