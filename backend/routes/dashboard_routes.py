from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.bike_service import BikeService
from services.ride_service import RideService
from models.models import db, User, Bike, Ride, RideRequest, RideMatch
from datetime import datetime, date

# Create namespace for user dashboard
dashboard_ns = Namespace('dashboard', description='📊 User Dashboard & Overview')

# Response models
dashboard_overview_model = dashboard_ns.model('DashboardOverview', {
    'user_profile': fields.Raw(description='User profile information'),
    'bike_summary': fields.Raw(description='Bike registration summary'),
    'ride_summary': fields.Raw(description='Ride activity summary'),
    'recent_activity': fields.Raw(description='Recent user activity'),
    'quick_stats': fields.Raw(description='Quick statistics')
})

user_activity_model = dashboard_ns.model('UserActivity', {
    'success': fields.Boolean(description='Operation success status'),
    'activities': fields.List(fields.Raw, description='List of recent activities'),
    'total_activities': fields.Integer(description='Total number of activities')
})

@dashboard_ns.route('/overview')
class DashboardOverview(Resource):
    @dashboard_ns.doc('get_dashboard_overview', security='Bearer')
    @dashboard_ns.response(200, '✅ Dashboard overview retrieved successfully')
    @dashboard_ns.response(404, '❌ User not found')
    @jwt_required()
    def get(self):
        """Get comprehensive dashboard overview for current user"""
        try:
            current_user_id = get_jwt_identity()
            
            # Get user
            user = User.query.get(current_user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}, 404
            
            # Get bike information safely
            try:
                bike_result = BikeService.get_user_bikes(current_user_id)
            except Exception as e:
                print(f"Bike service error: {e}")
                bike_result = {'total_bikes': 0, 'verified_bikes': 0, 'active_bike': None, 'bikes': []}
            
            # Get ride information safely
            try:
                user_rides_result = RideService.get_user_rides(current_user_id)
            except Exception as e:
                print(f"Ride service error: {e}")
                user_rides_result = {'rides': []}
            
            # Simple counts without complex relationships
            total_rides_offered = Ride.query.filter_by(rider_id=current_user_id).count()
            active_rides = Ride.query.filter_by(rider_id=current_user_id, status='active').count()
            
            # Basic statistics without complex calculations
            total_km_traveled = 0
            total_fuel_saved = 0
            
            dashboard_data = {
                'user_profile': {
                    'id': user.id,
                    'name': user.name,
                    'phone': user.phone,
                    'email': user.email,
                    'work_location': user.work_location,
                    'home_location': user.home_location,
                    'member_since': user.created_at.strftime('%B %Y') if user.created_at else None,
                    'rating': user.rating or 0.0,
                    'verification_status': {
                        'phone_verified': user.phone_verified,
                        'email_verified': user.email_verified
                    }
                },
                'bike_summary': {
                    'total_bikes': bike_result.get('total_bikes', 0),
                    'verified_bikes': bike_result.get('verified_bikes', 0),
                    'active_bike': bike_result.get('active_bike'),
                    'bikes': bike_result.get('bikes', [])
                },
                'ride_summary': {
                    'total_rides_offered': total_rides_offered,
                    'active_rides': active_rides,
                    'total_rides_taken': 0,  # Simplified for now
                    'pending_requests': 0,   # Simplified for now
                    'upcoming_as_rider': [],    # Simplified for now
                    'upcoming_as_passenger': [] # Simplified for now
                },
                'recent_activity': {
                    'recent_requests': [],  # Simplified for now
                    'recent_rides': []      # Simplified for now
                },
                'quick_stats': {
                    'total_km_traveled': total_km_traveled,
                    'total_fuel_cost_shared': round(total_fuel_saved, 2),
                    'rides_completed_this_month': 0,  # Simplified for now
                    'co2_saved_kg': round(total_fuel_saved * 0.1, 2)
                }
            }
            
            return {
                'success': True,
                'dashboard': dashboard_data
            }, 200
            
        except Exception as e:
            print(f"Dashboard error: {e}")
            return {'success': False, 'error': f'Failed to get dashboard overview: {str(e)}'}, 500

@dashboard_ns.route('/quick-stats')
class QuickStats(Resource):
    @dashboard_ns.doc('get_quick_stats', security='Bearer')
    @dashboard_ns.response(200, '✅ Quick stats retrieved successfully')
    @jwt_required()
    def get(self):
        """Get quick statistics for current user"""
        try:
            current_user_id = get_jwt_identity()
            
            # Count rides offered
            total_rides_offered = Ride.query.filter_by(rider_id=current_user_id).count()
            active_rides = Ride.query.filter_by(rider_id=current_user_id, is_active=True).count()
            
            # Count rides taken (as passenger)
            rides_taken = RideMatch.query.filter_by(passenger_id=current_user_id).count()
            
            # Count requests
            total_requests = RideRequest.query.filter_by(passenger_id=current_user_id).count()
            pending_requests = RideRequest.query.filter_by(passenger_id=current_user_id, status='pending').count()
            
            # Count bikes
            total_bikes = Bike.query.filter_by(user_id=current_user_id).count()
            verified_bikes = Bike.query.filter_by(user_id=current_user_id, is_verified=True).count()
            
            return {
                'success': True,
                'stats': {
                    'rides': {
                        'total_offered': total_rides_offered,
                        'active_rides': active_rides,
                        'total_taken': rides_taken
                    },
                    'requests': {
                        'total_sent': total_requests,
                        'pending': pending_requests
                    },
                    'bikes': {
                        'total_registered': total_bikes,
                        'verified': verified_bikes
                    }
                }
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get quick stats: {str(e)}'}, 500

@dashboard_ns.route('/activity')
class UserActivity(Resource):
    @dashboard_ns.doc('get_user_activity', security='Bearer')
    @dashboard_ns.response(200, '✅ User activity retrieved successfully')
    @jwt_required()
    def get(self):
        """Get recent user activity"""
        try:
            current_user_id = get_jwt_identity()
            limit = int(request.args.get('limit', 10))
            
            activities = []
            
            # Recent rides posted
            recent_rides = Ride.query.filter_by(rider_id=current_user_id).order_by(Ride.created_at.desc()).limit(limit // 2).all()
            for ride in recent_rides:
                activities.append({
                    'type': 'ride_posted',
                    'title': 'Posted a ride',
                    'description': f'From {ride.from_location} to {ride.to_location}',
                    'date': ride.created_at.isoformat(),
                    'data': {
                        'ride_id': ride.id,
                        'departure_date': ride.departure_date.isoformat(),
                        'available_seats': ride.available_seats
                    }
                })
            
            # Recent join requests
            recent_requests = RideRequest.query.filter_by(passenger_id=current_user_id).order_by(RideRequest.created_at.desc()).limit(limit // 2).all()
            for req in recent_requests:
                activities.append({
                    'type': 'join_request',
                    'title': 'Requested to join ride',
                    'description': f'From {req.ride.from_location} to {req.ride.to_location}',
                    'date': req.created_at.isoformat(),
                    'data': {
                        'request_id': req.id,
                        'status': req.status,
                        'ride_id': req.ride_id
                    }
                })
            
            # Sort activities by date
            activities.sort(key=lambda x: x['date'], reverse=True)
            activities = activities[:limit]
            
            return {
                'success': True,
                'activities': activities,
                'total_activities': len(activities)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get user activity: {str(e)}'}, 500

@dashboard_ns.route('/notifications')
class UserNotifications(Resource):
    @dashboard_ns.doc('get_notifications', security='Bearer')
    @dashboard_ns.response(200, '✅ Notifications retrieved successfully')
    @jwt_required()
    def get(self):
        """Get user notifications and alerts"""
        try:
            current_user_id = get_jwt_identity()
            
            notifications = []
            
            # Check for unverified bikes
            unverified_bikes = Bike.query.filter_by(user_id=current_user_id, is_verified=False).count()
            if unverified_bikes > 0:
                notifications.append({
                    'type': 'warning',
                    'title': 'Bike Verification Pending',
                    'message': f'You have {unverified_bikes} bike(s) pending admin verification.',
                    'action': 'Ensure all documents are properly uploaded.'
                })
            
            # Check for profile completion
            user = User.query.get(current_user_id)
            if not user.phone_verified:
                notifications.append({
                    'type': 'info',
                    'title': 'Verify Phone Number',
                    'message': 'Please verify your phone number to enhance account security.',
                    'action': 'Click to verify'
                })
            
            if not user.email_verified and user.email:
                notifications.append({
                    'type': 'info',
                    'title': 'Verify Email',
                    'message': 'Please verify your email address.',
                    'action': 'Click to verify'
                })
            
            # Check for pending requests on user's rides
            user_rides = Ride.query.filter_by(rider_id=current_user_id, is_active=True).all()
            pending_requests_count = 0
            for ride in user_rides:
                pending_requests_count += RideRequest.query.filter_by(ride_id=ride.id, status='pending').count()
            
            if pending_requests_count > 0:
                notifications.append({
                    'type': 'success',
                    'title': 'New Join Requests',
                    'message': f'You have {pending_requests_count} pending join request(s) for your rides.',
                    'action': 'Review requests'
                })
            
            return {
                'success': True,
                'notifications': notifications,
                'unread_count': len(notifications)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get notifications: {str(e)}'}, 500

# Configure JWT security for Swagger
dashboard_ns.authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter: Bearer {your-token-here}'
    }
} 