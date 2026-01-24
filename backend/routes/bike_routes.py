from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.bike_service import BikeService
from models.models import db, Bike
from datetime import datetime

# Create namespace for bike management
bike_ns = Namespace('bikes', description='🏍️ Bike Registration & Management')

# Define request/response models for Swagger documentation
bike_registration_model = bike_ns.model('BikeRegistration', {
    'bike_number': fields.String(required=True, description='Bike registration number', example='TN09AB1234'),
    'bike_type': fields.String(required=True, description='Type of bike', enum=['bike', 'scooter', 'motorcycle'], example='bike'),
    'brand': fields.String(required=True, description='Bike brand', example='Hero'),
    'model': fields.String(required=True, description='Bike model', example='Splendor Plus'),
    'color': fields.String(description='Bike color', example='Black'),
    'manufacture_year': fields.Integer(description='Year of manufacture', example=2020),
    'rc_number': fields.String(description='RC number (for verification)', example='TN09AB123456789'),
    'insurance_number': fields.String(description='Insurance policy number', example='POL123456789'),
    'rc_expiry': fields.String(description='RC expiry date (YYYY-MM-DD)', example='2025-12-31'),
    'insurance_expiry': fields.String(description='Insurance expiry date (YYYY-MM-DD)', example='2024-08-15')
})

bike_update_model = bike_ns.model('BikeUpdate', {
    'color': fields.String(description='Bike color'),
    'insurance_expiry': fields.String(description='Insurance expiry date (YYYY-MM-DD)'),
    'rc_expiry': fields.String(description='RC expiry date (YYYY-MM-DD)')
})

bike_validation_model = bike_ns.model('BikeValidation', {
    'bike_number': fields.String(required=True, description='Bike number to validate', example='TN09AB1234')
})

active_bike_model = bike_ns.model('ActiveBike', {
    'bike_id': fields.Integer(required=True, description='ID of bike to set as active', example=1)
})

# Response models
bike_response_model = bike_ns.model('BikeResponse', {
    'id': fields.Integer(description='Bike ID'),
    'bike_number': fields.String(description='Bike registration number'),
    'bike_type': fields.String(description='Type of bike'),
    'brand': fields.String(description='Bike brand'),
    'model': fields.String(description='Bike model'),
    'color': fields.String(description='Bike color'),
    'manufacture_year': fields.Integer(description='Year of manufacture'),
    'is_verified': fields.Boolean(description='Verification status'),
    'is_active': fields.Boolean(description='Active status'),
    'rc_number': fields.String(description='RC number'),
    'insurance_number': fields.String(description='Insurance number'),
    'rc_expiry': fields.String(description='RC expiry date'),
    'insurance_expiry': fields.String(description='Insurance expiry date'),
    'created_at': fields.String(description='Registration date')
})

bikes_list_response_model = bike_ns.model('BikesListResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'bikes': fields.List(fields.Nested(bike_response_model), description='List of bikes'),
    'total_bikes': fields.Integer(description='Total number of bikes'),
    'verified_bikes': fields.Integer(description='Number of verified bikes'),
    'active_bike': fields.Nested(bike_response_model, description='Currently active bike')
})

bike_success_response_model = bike_ns.model('BikeSuccessResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Success message'),
    'bike': fields.Nested(bike_response_model, description='Bike data')
})

bike_error_response_model = bike_ns.model('BikeErrorResponse', {
    'success': fields.Boolean(description='Operation success status', example=False),
    'error': fields.String(description='Error message'),
    'errors': fields.List(fields.String, description='List of validation errors')
})

validation_response_model = bike_ns.model('ValidationResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'validation': fields.Raw(description='Validation result data')
})

@bike_ns.route('/register')
class BikeRegistration(Resource):
    @bike_ns.doc('register_bike', security='Bearer')
    @bike_ns.expect(bike_registration_model)
    @bike_ns.response(201, '✅ Bike registered successfully')
    @bike_ns.response(400, '❌ Registration failed')
    @jwt_required()
    def post(self):
        """Register a new bike"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return {'success': False, 'error': 'No data provided'}, 400
            
            # Register bike using BikeService
            result = BikeService.register_bike(current_user_id, data)
            
            if result['success']:
                return result, 201
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Bike registration failed: {str(e)}'}, 500

@bike_ns.route('/')
class BikeList(Resource):
    @bike_ns.doc('get_user_bikes', security='Bearer')
    @bike_ns.response(200, '✅ Bikes retrieved successfully')
    @bike_ns.response(404, '❌ No bikes found')
    @jwt_required()
    def get(self):
        """Get all bikes registered by current user"""
        try:
            current_user_id = get_jwt_identity()
            result = BikeService.get_user_bikes(current_user_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 404
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get bikes: {str(e)}'}, 500

@bike_ns.route('/<int:bike_id>')
class BikeDetails(Resource):
    @bike_ns.doc('get_bike_details', security='Bearer')
    @bike_ns.response(200, '✅ Bike details retrieved successfully')
    @bike_ns.response(404, '❌ Bike not found')
    @jwt_required()
    def get(self, bike_id):
        """Get details of a specific bike"""
        try:
            current_user_id = get_jwt_identity()
            bike = Bike.query.filter_by(id=bike_id, user_id=current_user_id).first()
            
            if not bike:
                return {'success': False, 'error': 'Bike not found or not owned by user'}, 404
            
            return {'success': True, 'bike': bike.to_dict()}, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get bike details: {str(e)}'}, 500
    
    @bike_ns.doc('update_bike', security='Bearer')
    @bike_ns.expect(bike_update_model)
    @bike_ns.response(200, '✅ Bike updated successfully')
    @bike_ns.response(400, '❌ Update failed')
    @jwt_required()
    def put(self, bike_id):
        """Update bike information"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return {'success': False, 'error': 'No data provided'}, 400
            
            result = BikeService.update_bike(current_user_id, bike_id, data)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to update bike: {str(e)}'}, 500
    
    @bike_ns.doc('delete_bike', security='Bearer')
    @bike_ns.response(200, '✅ Bike deleted successfully')
    @bike_ns.response(400, '❌ Delete failed')
    @jwt_required()
    def delete(self, bike_id):
        """Delete a bike"""
        try:
            current_user_id = get_jwt_identity()
            result = BikeService.delete_bike(current_user_id, bike_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to delete bike: {str(e)}'}, 500

@bike_ns.route('/set-active')
class SetActiveBike(Resource):
    @bike_ns.doc('set_active_bike', security='Bearer')
    @bike_ns.expect(active_bike_model)
    @bike_ns.response(200, '✅ Active bike set successfully')
    @bike_ns.response(400, '❌ Failed to set active bike')
    @jwt_required()
    def post(self):
        """Set a bike as the active bike for rides"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or 'bike_id' not in data:
                return {'success': False, 'error': 'Bike ID is required'}, 400
            
            bike_id = data['bike_id']
            result = BikeService.set_active_bike(current_user_id, bike_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to set active bike: {str(e)}'}, 500

@bike_ns.route('/deactivate')
class DeactivateBike(Resource):
    @bike_ns.doc('deactivate_bike', security='Bearer')
    @bike_ns.expect(active_bike_model)
    @bike_ns.response(200, '✅ Bike deactivated successfully')
    @bike_ns.response(400, '❌ Failed to deactivate bike')
    @jwt_required()
    def post(self):
        """Deactivate a bike (user cannot post rides without active bike)"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or 'bike_id' not in data:
                return {'success': False, 'error': 'Bike ID is required'}, 400
            
            bike_id = data['bike_id']
            result = BikeService.deactivate_bike(current_user_id, bike_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to deactivate bike: {str(e)}'}, 500

@bike_ns.route('/validate-number')
class BikeNumberValidation(Resource):
    @bike_ns.doc('validate_bike_number')
    @bike_ns.expect(bike_validation_model)
    @bike_ns.response(200, '✅ Bike number validation result')
    def post(self):
        """Validate bike registration number format"""
        try:
            data = request.get_json()
            bike_number = data.get('bike_number') if data else None
            
            if not bike_number:
                return {'success': False, 'error': 'Bike number is required'}, 400
            
            result = BikeService.validate_bike_number(bike_number)
            
            # Check if bike number already exists
            if result['valid']:
                existing_bike = Bike.query.filter_by(bike_number=result['formatted_number']).first()
                result['available'] = existing_bike is None
                
            return {'success': True, 'validation': result}, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Bike number validation failed: {str(e)}'}, 500

@bike_ns.route('/stats')
class BikeStats(Resource):
    @bike_ns.doc('get_bike_stats', security='Bearer')
    @bike_ns.response(200, '✅ Bike statistics retrieved successfully')
    @jwt_required()
    def get(self):
        """Get bike statistics (admin endpoint)"""
        try:
            # TODO: Add admin role check here
            result = BikeService.get_bike_stats()
            
            if result['success']:
                return result, 200
            else:
                return result, 500
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get bike stats: {str(e)}'}, 500

@bike_ns.route('/verification-pending')
class PendingVerificationBikes(Resource):
    @bike_ns.doc('get_pending_bikes', security='Bearer')
    @bike_ns.response(200, '✅ Pending bikes retrieved successfully')
    @jwt_required()
    def get(self):
        """Get bikes pending verification (admin endpoint)"""
        try:
            # TODO: Add admin role check here
            pending_bikes = Bike.query.filter_by(is_verified=False).all()
            
            return {
                'success': True,
                'pending_bikes': [bike.to_dict() for bike in pending_bikes],
                'count': len(pending_bikes)
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get pending bikes: {str(e)}'}, 500

@bike_ns.route('/<int:bike_id>/verify')
class VerifyBike(Resource):
    @bike_ns.doc('verify_bike', security='Bearer')
    @bike_ns.response(200, '✅ Bike verified successfully')
    @bike_ns.response(400, '❌ Verification failed')
    @jwt_required()
    def post(self, bike_id):
        """Verify a bike (admin endpoint)"""
        try:
            # TODO: Add admin role check here
            bike = Bike.query.get(bike_id)
            
            if not bike:
                return {'success': False, 'error': 'Bike not found'}, 404
            
            if bike.is_verified:
                return {'success': False, 'error': 'Bike already verified'}, 400
            
            # Mark as verified
            bike.is_verified = True
            bike.verified_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Bike {bike.bike_number} verified successfully',
                'bike': bike.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to verify bike: {str(e)}'}, 500

# Configure JWT security for Swagger
bike_ns.authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter: Bearer {your-token-here}'
    }
} 