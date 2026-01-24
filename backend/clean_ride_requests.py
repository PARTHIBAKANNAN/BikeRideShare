#!/usr/bin/env python3
"""
Clean up existing ride requests to fix duplicate join issue
"""

from models.models import db, RideRequest, Ride, User
from app import create_app

def clean_ride_requests():
    app = create_app('development')
    with app.app_context():
        print('=== CLEANING RIDE REQUESTS ===')
        
        # Get all ride requests
        requests = RideRequest.query.all()
        print(f'Total ride requests: {len(requests)}')
        
        for req in requests:
            passenger = User.query.get(req.passenger_id)
            ride = Ride.query.get(req.ride_id) if req.ride_id else None
            
            print(f'Request {req.id}:')
            print(f'  Passenger: {passenger.name if passenger else "Unknown"} (ID: {req.passenger_id})')
            print(f'  Ride: {req.ride_id}')
            print(f'  Status: {req.status}')
            print(f'  Created: {req.created_at}')
        
        # Clean up old requests for testing
        print('\n🧹 Cleaning up old ride requests for testing...')
        old_requests = RideRequest.query.filter_by(status='pending').all()
        
        for req in old_requests:
            print(f'  Deleting request {req.id}')
            db.session.delete(req)
        
        db.session.commit()
        print(f'✅ Deleted {len(old_requests)} pending requests')
        
        # Verify cleanup
        remaining = RideRequest.query.count()
        print(f'📊 Remaining requests: {remaining}')

if __name__ == "__main__":
    clean_ride_requests() 