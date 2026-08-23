from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from models.models import db, User
from datetime import datetime

# Create namespace for authentication
auth_ns = Namespace('auth', description='🔐 User Authentication Operations')

# Define request/response models for Swagger documentation
user_registration_model = auth_ns.model('UserRegistration', {
    'name': fields.String(required=True, description='Full name', example='Ravi Kumar'),
    'phone': fields.String(required=True, description='Phone number with country code', example='+919876543210'),
    'email': fields.String(description='Email address (optional)', example='ravi@gmail.com'),
    'gender': fields.String(description='Gender (female/male/other/prefer_not_to_say)', example='female'),
    'aadhaar_number': fields.String(required=True, description='12-digit Aadhaar number (immutable)', example='123456789012'),
    'date_of_birth': fields.String(description='Date of birth (YYYY-MM-DD)', example='1998-05-15'),
    'avatar': fields.String(description='Avatar identifier', example='avatar-1'),
    'password': fields.String(required=True, description='Password (min 6 chars)', example='SecurePass123!'),
    'work_location': fields.String(required=True, description='Work location in Chennai', example='Sholinganallur'),
    'home_location': fields.String(required=True, description='Home location in Chennai', example='Tambaram')
})

user_login_model = auth_ns.model('UserLogin', {
    'phone_or_email': fields.String(required=True, description='Phone number or email address', example='+919876543210'),
    'password': fields.String(required=True, description='Password', example='SecurePass123!')
})

user_profile_update_model = auth_ns.model('UserProfileUpdate', {
    'name': fields.String(description='Full name'),
    'phone': fields.String(description='Phone number'),
    'email': fields.String(description='Email address'),
    'avatar': fields.String(description='Avatar identifier'),
    'gender': fields.String(description='Gender'),
    'work_location': fields.String(description='Work location'),
    'home_location': fields.String(description='Home location'),
    'preferred_departure_time': fields.String(description='Preferred departure time (HH:MM)', example='08:30'),
    'travel_days': fields.List(fields.String, description='Travel days', example=['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
})

password_change_model = auth_ns.model('PasswordChange', {
    'current_password': fields.String(required=True, description='Current password'),
    'new_password': fields.String(required=True, description='New password (must meet strength requirements)')
})

validation_request_model = auth_ns.model('ValidationRequest', {
    'phone': fields.String(description='Phone number to validate', example='+919876543210'),
    'email': fields.String(description='Email to validate', example='user@gmail.com')
})

token_verification_model = auth_ns.model('TokenVerification', {
    'token': fields.String(required=True, description='JWT token to verify')
})

# Response models
user_response_model = auth_ns.model('UserResponse', {
    'id': fields.Integer(description='User ID'),
    'name': fields.String(description='Full name'),
    'phone': fields.String(description='Phone number'),
    'email': fields.String(description='Email address'),
    'work_location': fields.String(description='Work location'),
    'home_location': fields.String(description='Home location'),
    'preferred_departure_time': fields.String(description='Preferred departure time'),
    'travel_days': fields.List(fields.String, description='Travel days'),
    'phone_verified': fields.Boolean(description='Phone verification status'),
    'email_verified': fields.Boolean(description='Email verification status'),
    'rating': fields.Float(description='User rating'),
    'total_rides_offered': fields.Integer(description='Total rides offered'),
    'total_rides_taken': fields.Integer(description='Total rides taken'),
    'is_active': fields.Boolean(description='Account status'),
    'created_at': fields.String(description='Account creation date')
})

success_response_model = auth_ns.model('SuccessResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'message': fields.String(description='Success message'),
    'user': fields.Nested(user_response_model, description='User data'),
    'token': fields.String(description='JWT authentication token')
})

error_response_model = auth_ns.model('ErrorResponse', {
    'success': fields.Boolean(description='Operation success status', example=False),
    'error': fields.String(description='Error message'),
    'errors': fields.List(fields.String, description='List of validation errors')
})

validation_response_model = auth_ns.model('ValidationResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'validation': fields.Raw(description='Validation result data')
})

@auth_ns.route('/register')
class UserRegistration(Resource):
    @auth_ns.doc('register_user')
    @auth_ns.expect(user_registration_model)
    @auth_ns.response(201, '✅ User registered successfully')
    @auth_ns.response(400, '❌ Registration failed')
    def post(self):
        """Register a new user account"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'error': 'No data provided'}, 400
            
            # Register user using AuthService
            result = AuthService.register_user(data)
            
            if result['success']:
                return result, 201
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Registration failed: {str(e)}'}, 500

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.doc('login_user')
    @auth_ns.expect(user_login_model)
    @auth_ns.response(200, '✅ Login successful')
    @auth_ns.response(401, '❌ Login failed')
    def post(self):
        """Authenticate user login"""
        try:
            data = request.get_json()
            
            if not data:
                return {'success': False, 'error': 'No data provided'}, 400
            
            # Login user using AuthService
            result = AuthService.login_user(data)
            
            if result['success']:
                return result, 200
            else:
                return result, 401
                
        except Exception as e:
            return {'success': False, 'error': f'Login failed: {str(e)}'}, 500

@auth_ns.route('/profile')
class UserProfile(Resource):
    @auth_ns.doc('get_profile', security='Bearer')
    @auth_ns.response(200, '✅ Profile retrieved successfully')
    @auth_ns.response(404, '❌ User not found')
    @jwt_required()
    def get(self):
        """Get current user profile (requires authentication)"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return {'success': False, 'error': 'User not found'}, 404
            
            return {'success': True, 'user': user.to_dict()}, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get profile: {str(e)}'}, 500
    
    @auth_ns.doc('update_profile', security='Bearer')
    @auth_ns.expect(user_profile_update_model)
    @auth_ns.response(200, '✅ Profile updated successfully')
    @auth_ns.response(400, '❌ Update failed')
    @jwt_required()
    def put(self):
        """Update user profile (requires authentication)"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return {'success': False, 'error': 'User not found'}, 404
            
            data = request.get_json()
            if not data:
                return {'success': False, 'error': 'No data provided'}, 400
            
            # Update allowed fields
            allowed_fields = ['name', 'work_location', 'home_location', 'preferred_departure_time', 'travel_days']
            
            for field in allowed_fields:
                if field in data:
                    if field == 'preferred_departure_time' and data[field]:
                        try:
                            time_obj = datetime.strptime(data[field], '%H:%M').time()
                            setattr(user, field, time_obj)
                        except ValueError:
                            return {'success': False, 'error': 'Invalid time format. Use HH:MM'}, 400
                    elif field == 'travel_days' and data[field]:
                        user.set_travel_days(data[field])
                    else:
                        setattr(user, field, data[field])
            
            db.session.commit()
            
            return {'success': True, 'message': 'Profile updated successfully', 'user': user.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to update profile: {str(e)}'}, 500

@auth_ns.route('/change-password')
class PasswordChange(Resource):
    @auth_ns.doc('change_password', security='Bearer')
    @auth_ns.expect(password_change_model)
    @auth_ns.response(200, '✅ Password changed successfully')
    @auth_ns.response(400, '❌ Password change failed')
    @jwt_required()
    def post(self):
        """Change user password (requires authentication)"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return {'success': False, 'error': 'User not found'}, 404
            
            data = request.get_json()
            if not data:
                return {'success': False, 'error': 'No data provided'}, 400
            
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            if not current_password or not new_password:
                return {'success': False, 'error': 'Both current and new passwords are required'}, 400
            
            # Verify current password
            if not AuthService.verify_password(current_password, user.password_hash):
                return {'success': False, 'error': 'Current password is incorrect'}, 400
            
            # Validate new password strength
            password_validation = AuthService.validate_password_strength(new_password)
            if not password_validation['valid']:
                return {'success': False, 'errors': password_validation['errors']}, 400
            
            # Update password
            user.password_hash = AuthService.hash_password(new_password)
            db.session.commit()
            
            return {'success': True, 'message': 'Password changed successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to change password: {str(e)}'}, 500

@auth_ns.route('/verify-token')
class TokenVerification(Resource):
    @auth_ns.doc('verify_token')
    @auth_ns.expect(token_verification_model)
    @auth_ns.response(200, '✅ Token is valid')
    @auth_ns.response(401, '❌ Token is invalid')
    def post(self):
        """Verify JWT token validity"""
        try:
            data = request.get_json()
            token = data.get('token') if data else None
            
            if not token:
                return {'success': False, 'error': 'Token is required'}, 400
            
            result = AuthService.get_user_from_token(token)
            
            if result['success']:
                return result, 200
            else:
                return result, 401
                
        except Exception as e:
            return {'success': False, 'error': f'Token verification failed: {str(e)}'}, 500

@auth_ns.route('/refresh-token')
class TokenRefresh(Resource):
    @auth_ns.doc('refresh_token', security='Bearer')
    @auth_ns.response(200, '✅ Token refreshed successfully')
    @auth_ns.response(404, '❌ User not found')
    @jwt_required()
    def post(self):
        """Refresh JWT token (requires authentication)"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return {'success': False, 'error': 'User not found or inactive'}, 404
            
            # Generate new token
            new_token = AuthService.generate_jwt_token(user.id)
            
            return {
                'success': True, 
                'message': 'Token refreshed successfully', 
                'token': new_token, 
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            return {'success': False, 'error': f'Token refresh failed: {str(e)}'}, 500

# License verification models
license_submission_model = auth_ns.model('LicenseSubmission', {
    'license_number': fields.String(required=True, description='Driving license number', example='DL1420110012345'),
    'license_image_url': fields.String(description='URL to uploaded license image (optional)', example='https://example.com/license.jpg')
})

profile_update_model = auth_ns.model('ProfileUpdate', {
    'name': fields.String(description='Full name', example='John Doe'),
    'work_location': fields.String(description='Work location', example='T. Nagar'),
    'home_location': fields.String(description='Home location', example='Adyar')
})

@auth_ns.route('/license/submit')
class LicenseSubmission(Resource):
    @auth_ns.doc('submit_license_verification', security='Bearer')
    @auth_ns.expect(license_submission_model)
    @auth_ns.response(201, '✅ License submitted for verification')
    @auth_ns.response(400, '❌ Validation error')
    @auth_ns.response(401, '❌ Authentication required')
    @jwt_required()
    def post(self):
        """Submit driving license for admin verification"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            result = AuthService.submit_license_verification(current_user_id, data)
            
            if result['success']:
                return result, 201
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'License submission failed: {str(e)}'}, 500

@auth_ns.route('/verification-status')
class VerificationStatus(Resource):
    @auth_ns.doc('get_verification_status', security='Bearer')
    @auth_ns.response(200, '✅ Verification status retrieved')
    @auth_ns.response(401, '❌ Authentication required')
    @jwt_required()
    def get(self):
        """Get user's verification status for posting rides"""
        try:
            current_user_id = get_jwt_identity()
            
            result = AuthService.get_verification_status(current_user_id)
            
            if result['success']:
                return result, 200
            else:
                return result, 404
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to get verification status: {str(e)}'}, 500

@auth_ns.route('/profile')
class UserProfile(Resource):
    @auth_ns.doc('get_user_profile', security='Bearer')
    @auth_ns.response(200, '✅ Profile retrieved successfully')
    @auth_ns.response(401, '❌ Authentication required')
    @jwt_required()
    def get(self):
        """Get current user's profile"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return {'success': False, 'error': 'User not found or inactive'}, 404
            
            return {
                'success': True,
                'user': user.to_dict()
            }, 200
        except Exception as e:
            return {'success': False, 'error': f'Failed to get profile: {str(e)}'}, 500

    @auth_ns.doc('update_user_profile_main', security='Bearer')
    @auth_ns.expect(profile_update_model)
    @auth_ns.response(200, '✅ Profile updated successfully')
    @auth_ns.response(400, '❌ Validation error')
    @auth_ns.response(401, '❌ Authentication required')
    @jwt_required()
    def put(self):
        """Update current user's profile"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            result = AuthService.update_profile(current_user_id, data)
            if result['success']:
                return result, 200
            else:
                return result, 400
        except Exception as e:
            return {'success': False, 'error': f'Profile update failed: {str(e)}'}, 500

@auth_ns.route('/profile/update')
class UpdateProfile(Resource):
    @auth_ns.doc('update_user_profile', security='Bearer')
    @auth_ns.expect(profile_update_model)
    @auth_ns.response(200, '✅ Profile updated successfully')
    @auth_ns.response(400, '❌ Validation error')
    @auth_ns.response(401, '❌ Authentication required')
    @jwt_required()
    def put(self):
        """Update user profile information"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            result = AuthService.update_profile(current_user_id, data)
            
            if result['success']:
                return result, 200
            else:
                return result, 400
                
        except Exception as e:
            return {'success': False, 'error': f'Profile update failed: {str(e)}'}, 500

# Configure JWT security for Swagger
auth_ns.authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Enter: Bearer {your-token-here}'
    }
} 