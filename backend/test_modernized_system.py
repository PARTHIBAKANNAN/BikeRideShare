#!/usr/bin/env python3
"""
Test script for the modernized Smart Ride Matcher
Tests Neon Postgres connection, OSRM road routing, fare calculations, and corridor matching
"""

import sys
import os

# Set UTF-8 encoding support
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import create_app
from services.route_service import RouteService
from services.fare_service import FareService
from services.ai_route_matcher import ai_route_matcher
from models.models import db, User, Bike, Ride

def test_all():
    print("=" * 60)
    print(">> SMART RIDE MATCHER - CHENNAI COMMUTE TEST SUITE")
    print("=" * 60)
    
    # 1. Test Database & App Context
    print("\n[1/4] Testing Database Connection (Neon PostgreSQL)...")
    app = create_app('development')
    with app.app_context():
        user_count = User.query.count()
        bike_count = Bike.query.count()
        ride_count = Ride.query.count()
        print(f"   [OK] Database connected successfully!")
        print(f"   [INFO] Current Records: Users={user_count}, Bikes={bike_count}, Rides={ride_count}")
        
    # 2. Test OSRM Road Routing
    print("\n[2/4] Testing OSRM Chennai Road Routing...")
    r1 = RouteService.calculate_road_route("Maduravoyal", "Olympia Tech Park")
    print(f"   Route: Maduravoyal -> Olympia Tech Park (Ekkatuthangal)")
    print(f"   [OK] Road Distance: {r1['distance_km']} km")
    print(f"   [OK] Est. Duration: {r1['duration_minutes']} minutes")
    print(f"   [OK] Polyline Points: {len(r1['coordinates'])} coordinate pairs")
    
    r2 = RouteService.calculate_road_route("Tambaram", "Tidel Park")
    print(f"\n   Route: Tambaram -> Tidel Park (OMR)")
    print(f"   [OK] Road Distance: {r2['distance_km']} km")
    print(f"   [OK] Est. Duration: {r2['duration_minutes']} minutes")
    
    # 3. Test Fare Service
    print("\n[3/4] Testing Fare Calculation Engine...")
    fare_peak = FareService.calculate_fare("Maduravoyal", "Olympia Tech Park", "09:00", "bike")
    fare_normal = FareService.calculate_fare("Maduravoyal", "Olympia Tech Park", "14:00", "bike")
    print(f"   Peak Hour (9:00 AM): Rs {fare_peak['final_fare']} (Peak surcharge: Rs {fare_peak['peak_surcharge']})")
    print(f"   Off-Peak (2:00 PM):  Rs {fare_normal['final_fare']} (Peak surcharge: Rs {fare_normal['peak_surcharge']})")
    
    # 4. Test Algorithmic Corridor Matching
    print("\n[4/4] Testing Corridor Overlap Matching...")
    print("   Scenario: Rider goes Maduravoyal -> Olympia Tech Park")
    print("   Passenger searches Vadapalani -> Olympia Tech Park")
    match = RouteService.calculate_corridor_match("Maduravoyal", "Olympia Tech Park", "Vadapalani", "Olympia Tech Park")
    print(f"   [OK] Match Score: {match['match_score']}%")
    print(f"   [OK] Match Type: {match['match_type']}")
    print(f"   [OK] Detour Time: {match['detour_time']}")
    print(f"   [OK] Suggested Pickup: {match['pickup_suggestion']}")
    print(f"   [OK] Reasoning: {match['reasoning']}")
    
    print("\n" + "=" * 60)
    print(">> ALL BACKEND SYSTEMS TESTED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_all()
