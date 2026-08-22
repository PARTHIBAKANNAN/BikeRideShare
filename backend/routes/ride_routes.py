from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.ride_service import RideService
from models.models import db, Ride, RideRequest
from datetime import datetime

# Create namespace for ride management
ride_ns = Namespace('rides', description='🛣️ Ride Posting & Searching')

# Define request/response models for Swagger documentation
ride_post_model = ride_ns.model('RidePost', {
    'from_location': fields.String(required=True, description='Starting location', example='Tambaram'),
    'to_location': fields.String(required=True, description='Destination location', example='Sholinganallur'),
    'departure_date': fields.String(required=True, description='Departure date (YYYY-MM-DD)', example='2025-08-04'),
    'departure_time': fields.String(required=True, description='Departure time (HH:MM)', example='08:30'),
    'available_seats': fields.Integer(description='Number of available seats', example=2, min=1, max=3),
    'fuel_cost': fields.Float(description='Fuel cost to be shared (₹)', example=50.0),
    'description': fields.String(description='Additional details about the ride', example='Daily office commute via OMR'),
    'is_recurring': fields.Boolean(description='Is this a recurring ride?', example=False),
    'recurring_days': fields.List(fields.String, description='Days for recurring ride', example=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
})

ride_search_model = ride_ns.model('RideSearch', {
    'from_location': fields.String(description='Starting location (partial match)', example='Tambaram'),
    'to_location': fields.String(description='Destination location (partial match)', example='Sholinganallur'),
    'travel_date': fields.String(description='Travel date (YYYY-MM-DD)', example='2025-08-04'),
    'max_cost': fields.Float(description='Maximum acceptable fuel cost', example=100.0),
    'min_seats': fields.Integer(description='Minimum required seats', example=1)
})

ride_join_request_model = ride_ns.model('RideJoinRequest', {
    'message': fields.String(description='Message to the rider', example='Hi! I would like to join your ride.'),
    'pickup_location': fields.String(description='Preferred pickup location', example='Tambaram Bus Stand')
})

request_response_model = ride_ns.model('RequestResponse', {
    'response': fields.String(required=True, description='Response to the request', enum=['accepted', 'rejected'], example='accepted')
})

ride_cancel_model = ride_ns.model('RideCancel', {
    'reason': fields.String(description='Reason for cancellation', example='Emergency came up')
})

# Response models
ride_response_model = ride_ns.model('RideResponse', {
    'id': fields.Integer(description='Ride ID'),
    'rider_id': fields.Integer(description='Rider user ID'),
    'rider_name': fields.String(description='Rider name'),
    'bike_info': fields.Raw(description='Bike information'),
    'from_location': fields.String(description='Starting location'),
    'to_location': fields.String(description='Destination location'),
    'departure_date': fields.String(description='Departure date'),
    'departure_time': fields.String(description='Departure time'),
    'available_seats': fields.Integer(description='Available seats'),
    'fuel_cost': fields.Float(description='Fuel cost'),
    'description': fields.String(description='Ride description'),
    'is_recurring': fields.Boolean(description='Is recurring ride'),
    'recurring_days': fields.List(fields.String, description='Recurring days'),
    'status': fields.String(description='Ride status (active/completed/cancelled)'),
    'created_at': fields.String(description='Created date')
})

ride_request_response_model = ride_ns.model('RideRequestResponse', {
    'id': fields.Integer(description='Request ID'),
    'passenger_id': fields.Integer(description='Passenger user ID'),
    'passenger_name': fields.String(description='Passenger name'),
    'ride_id': fields.Integer(description='Ride ID'),
    'message': fields.String(description='Request message'),
    'pickup_location': fields.String(description='Pickup location'),
    'status': fields.String(description='Request status'),
    'created_at': fields.String(description='Request date')
})

ride_success_response_model = ride_ns.model('RideSuccessResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Success message'),
    'ride': fields.Nested(ride_response_model, description='Ride data')
})

rides_list_response_model = ride_ns.model('RidesListResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'rides': fields.List(fields.Nested(ride_response_model), description='List of rides'),
    'total_results': fields.Integer(description='Total number of results'),
    'search_criteria': fields.Raw(description='Search criteria used')
})

ride_error_response_model = ride_ns.model('RideErrorResponse', {
    'success': fields.Boolean(description='Operation success status', example=False),
    'error': fields.String(description='Error message'),
    'errors': fields.List(fields.String, description='List of validation errors')
})

@ride_ns.route('/post')
class PostRide(Resource):
    @ride_ns.doc('post_ride', security='Bearer')
    @ride_ns.expect(ride_post_model)
    @ride_ns.response(201, '✅ Ride posted successfully')
    @ride_ns.response(400, '❌ Failed to post ride')
    @jwt_required()
    def post(self):
        """Post a new ride offer"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return {'success': False, 'error': 'No data provided'}, 400
            
            # Post ride using RideService
            result = RideService.post_ride(current_user_id, data)
            
            if result['success']:
                return result, 201
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to post ride: {str(e)}'}, 500

@ride_ns.route('/search')
class SearchRides(Resource):
    @ride_ns.doc('search_rides')
    @ride_ns.expect(ride_search_model)
    @ride_ns.response(200, '✅ Rides search completed')
    def post(self):
        """Search for available rides"""
        try:
            data = request.get_json() or {}
            
            # Get current user ID if authenticated (to exclude their rides)
            current_user_id = None
            try:
                current_user_id = get_jwt_identity()
            except:
                pass  # User not authenticated, search all rides
            
            result = RideService.search_rides(data, current_user_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to search rides: {str(e)}'}, 500

@ride_ns.route('/my-rides')
class MyRides(Resource):
    @ride_ns.doc('get_my_rides', security='Bearer')
    @ride_ns.response(200, '✅ User rides retrieved successfully')
    @jwt_required()
    def get(self):
        """Get all rides posted by current user"""
        try:
            current_user_id = get_jwt_identity()
            ride_type = request.args.get('type', 'all')  # all, active, completed, upcoming
            
            result = RideService.get_user_rides(current_user_id, ride_type)
            
            if result['success']:
                return result, 200
            else:
                return result, 404
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get rides: {str(e)}'}, 500

@ride_ns.route('/<int:ride_id>')
class RideDetails(Resource):
    @ride_ns.doc('get_ride_details')
    @ride_ns.response(200, '✅ Ride details retrieved successfully')
    @ride_ns.response(404, '❌ Ride not found')
    def get(self, ride_id):
        """Get details of a specific ride"""
        try:
            ride = Ride.query.get(ride_id)
            
            if not ride:
                return {'success': False, 'error': 'Ride not found'}, 404
            
            return {'success': True, 'ride': ride.to_dict()}, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get ride details: {str(e)}'}, 500

@ride_ns.route('/<int:ride_id>/join')
class JoinRide(Resource):
    @ride_ns.doc('join_ride', security='Bearer')
    @ride_ns.expect(ride_join_request_model)
    @ride_ns.response(201, '✅ Join request sent successfully')
    @ride_ns.response(400, '❌ Failed to join ride')
    @jwt_required()
    def post(self, ride_id):
        """Request to join a ride"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json() or {}
            
            result = RideService.request_ride_join(current_user_id, ride_id, data)
            
            if result['success']:
                return result, 201
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to join ride: {str(e)}'}, 500

@ride_ns.route('/<int:ride_id>/requests')
class RideRequests(Resource):
    @ride_ns.doc('get_ride_requests', security='Bearer')
    @ride_ns.response(200, '✅ Ride requests retrieved successfully')
    @ride_ns.response(403, '❌ Not authorized to view requests')
    @jwt_required()
    def get(self, ride_id):
        """Get join requests for a ride (only ride owner)"""
        try:
            current_user_id = get_jwt_identity()
            
            result = RideService.get_ride_requests(current_user_id, ride_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 403
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get ride requests: {str(e)}'}, 500

@ride_ns.route('/requests/<int:request_id>/respond')
class RespondToRequest(Resource):
    @ride_ns.doc('respond_to_request', security='Bearer')
    @ride_ns.expect(request_response_model)
    @ride_ns.response(200, '✅ Response sent successfully')
    @ride_ns.response(400, '❌ Failed to respond')
    @jwt_required()
    def post(self, request_id):
        """Accept or reject a ride join request"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or 'response' not in data:
                return {'success': False, 'error': 'Response is required'}, 400
            
            response = data['response']
            result = RideService.respond_to_request(current_user_id, request_id, response)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to respond to request: {str(e)}'}, 500

@ride_ns.route('/<int:ride_id>/cancel')
class CancelRide(Resource):
    @ride_ns.doc('cancel_ride', security='Bearer')
    @ride_ns.expect(ride_cancel_model)
    @ride_ns.response(200, '✅ Ride cancelled successfully')
    @ride_ns.response(400, '❌ Failed to cancel ride')
    @jwt_required()
    def post(self, ride_id):
        """Cancel a ride (only ride owner)"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json() or {}
            reason = data.get('reason')
            
            result = RideService.cancel_ride(current_user_id, ride_id, reason)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to cancel ride: {str(e)}'}, 500

@ride_ns.route('/history')
class RideHistory(Resource):
    @ride_ns.doc('get_ride_history', security='Bearer')
    @ride_ns.response(200, '✅ Ride history retrieved successfully')
    @jwt_required()
    def get(self):
        """Get complete ride history for current user"""
        try:
            current_user_id = get_jwt_identity()
            
            result = RideService.get_user_ride_history(current_user_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 500
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get ride history: {str(e)}'}, 500

@ride_ns.route('/my-requests')
class MyRequests(Resource):
    @ride_ns.doc('get_my_requests', security='Bearer')
    @ride_ns.response(200, '✅ User requests retrieved successfully')
    @jwt_required()
    def get(self):
        """Get all ride requests made by current user"""
        try:
            current_user_id = get_jwt_identity()
            
            # Get all requests made by user
            requests = RideRequest.query.filter_by(passenger_id=current_user_id).all()
            
            return {
                'success': True,
                'requests': [request.to_dict() for request in requests],
                'total_requests': len(requests),
                'pending_requests': len([r for r in requests if r.status == 'pending']),
                'accepted_requests': len([r for r in requests if r.status == 'accepted']),
                'rejected_requests': len([r for r in requests if r.status == 'rejected'])
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get requests: {str(e)}'}, 500

@ride_ns.route('/stats')
class RideStats(Resource):
    @ride_ns.doc('get_ride_stats', security='Bearer')
    @ride_ns.response(200, '✅ Ride statistics retrieved successfully')
    @jwt_required()
    def get(self):
        """Get ride statistics (admin endpoint)"""
        try:
            # TODO: Add admin role check here
            result = RideService.get_ride_stats()
            
            if result['success']:
                return result, 200
            else:
                return result, 500
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get ride stats: {str(e)}'}, 500

@ride_ns.route('/popular-routes')
class PopularRoutes(Resource):
    @ride_ns.doc('get_popular_routes')
    @ride_ns.response(200, '✅ Popular routes retrieved successfully')
    def get(self):
        """Get most popular ride routes"""
        try:
            from sqlalchemy import func
            from models.models import Ride
            
            # Get top 20 popular routes
            popular_routes = db.session.query(
                Ride.from_location,
                Ride.to_location,
                func.count(Ride.id).label('ride_count')
            ).group_by(
                Ride.from_location, 
                Ride.to_location
            ).order_by(
                func.count(Ride.id).desc()
            ).limit(20).all()
            
            return {
                'success': True,
                'popular_routes': [
                    {
                        'from_location': route.from_location,
                        'to_location': route.to_location,
                        'ride_count': route.ride_count
                    } for route in popular_routes
                ],
                'total_routes': len(popular_routes)
            }, 200
        except Exception as e:
            return {'success': False, 'error': f'Failed to get popular routes: {str(e)}'}, 500

@ride_ns.route('/route-preview')
class RoutePreview(Resource):
    @ride_ns.doc('get_route_preview')
    @ride_ns.response(200, '✅ Route preview calculated successfully')
    def post(self):
        """Calculate road route polyline, distance, duration, and fare preview"""
        try:
            from services.route_service import RouteService
            from services.fare_service import FareService
            
            data = request.get_json() or {}
            from_loc = data.get('from_location', '').strip()
            to_loc = data.get('to_location', '').strip()
            dep_time = data.get('departure_time')
            bike_type = data.get('bike_type', 'bike')
            
            if not from_loc or not to_loc:
                return {'success': False, 'error': 'Both from_location and to_location are required'}, 400
                
            route_info = RouteService.calculate_road_route(from_loc, to_loc)
            fare_info = FareService.calculate_fare(from_loc, to_loc, dep_time, bike_type)
            
            return {
                'success': True,
                'from_location': from_loc,
                'to_location': to_loc,
                'from_coords': route_info.get('from_coords'),
                'to_coords': route_info.get('to_coords'),
                'distance_km': route_info.get('distance_km'),
                'duration_minutes': route_info.get('duration_minutes'),
                'coordinates': route_info.get('coordinates', []),
                'geojson': route_info.get('geojson'),
                'fare': fare_info
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to calculate route preview: {str(e)}'}, 500

@ride_ns.route('/chennai-locations')
class ChennaiLocations(Resource):
    @ride_ns.doc('get_chennai_locations')
    @ride_ns.response(200, '✅ Chennai locations retrieved successfully')
    def get(self):
        """Get pre-seeded Chennai commuter locations for autocomplete"""
        try:
            from services.route_service import RouteService
            query = request.args.get('q', '')
            locations = RouteService.get_locations_list(query)
            return {'success': True, 'locations': locations, 'count': len(locations)}, 200
        except Exception as e:
            return {'success': False, 'error': f'Failed to get locations: {str(e)}'}, 500

@ride_ns.route('/reverse-geocode')
class ReverseGeocode(Resource):
    @ride_ns.doc('reverse_geocode_coordinates')
    @ride_ns.response(200, '✅ Coordinates reverse geocoded successfully')
    def get(self):
        """Reverse geocode GPS coordinates (lat, lng) to Chennai address and pincode"""
        try:
            from services.route_service import RouteService
            lat = float(request.args.get('lat', 13.0827))
            lng = float(request.args.get('lng', 80.2707))
            result = RouteService.reverse_geocode(lat, lng)
            return result, 200
        except Exception as e:
            return {'success': False, 'error': f'Failed to reverse geocode: {str(e)}'}, 500

# Configure JWT security for Swagger
ride_ns.authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter: Bearer {your-token-here}'
    }
} 