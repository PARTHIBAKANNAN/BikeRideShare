import bcrypt
import jwt
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta
from flask import current_app
import re


class AuthService:
    """Authentication service for user registration, login, and validation"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def generate_jwt_token(user_id: int, expires_in_hours: int = 24) -> str:
        """Generate JWT token for user authentication"""
        payload = {
            'sub': str(user_id),  # Flask-JWT-Extended expects 'sub' claim
            'user_id': user_id,   # Keep for backward compatibility
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'default-secret-key')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        """Decode and validate JWT token"""
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'default-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Handle both 'sub' and 'user_id' for compatibility
            user_id = payload.get('user_id') or int(payload.get('sub', 0))
            
            return {'valid': True, 'user_id': user_id}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}
    
    @staticmethod
    def validate_phone_number(phone: str, country_code: str = 'IN') -> dict:
        """Validate phone number format"""
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(phone, country_code)
            
            # Check if valid
            if phonenumbers.is_valid_number(parsed_number):
                formatted_number = phonenumbers.format_number(
                    parsed_number, 
                    phonenumbers.PhoneNumberFormat.E164
                )
                return {
                    'valid': True,
                    'formatted_number': formatted_number,
                    'country_code': parsed_number.country_code,
                    'national_number': parsed_number.national_number
                }
            else:
                return {'valid': False, 'error': 'Invalid phone number format'}
                
        except phonenumbers.NumberParseException as e:
            return {'valid': False, 'error': f'Phone number parsing error: {str(e)}'}
    
    @staticmethod
    def validate_email_address(email: str) -> dict:
        """Validate email address format"""
        try:
            # Validate email
            validated_email = validate_email(email)
            return {
                'valid': True,
                'email': validated_email.email,
                'normalized': validated_email.email.lower()
            }
        except EmailNotValidError as e:
            return {'valid': False, 'error': str(e)}
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': 'strong' if len(errors) == 0 else 'weak'
        }
    
    @staticmethod
    def register_user(user_data: dict) -> dict:
        """Register a new user with validation"""
        from models.models import db, User  # Import here to avoid circular imports
        
        # Extract user data
        name = user_data.get('name', '').strip()
        phone = user_data.get('phone', '').strip()
        email = user_data.get('email', '').strip()
        password = user_data.get('password', '')
        work_location = user_data.get('work_location', '').strip()
        home_location = user_data.get('home_location', '').strip()
        
        # Validation
        errors = []
        
        # Name validation
        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters long")
        
        # Phone validation
        phone_validation = AuthService.validate_phone_number(phone)
        if not phone_validation['valid']:
            errors.append(f"Phone: {phone_validation['error']}")
        else:
            formatted_phone = phone_validation['formatted_number']
            # Check if phone already exists
            if User.query.filter_by(phone=formatted_phone).first():
                errors.append("Phone number already registered")
        
        # Email validation (optional)
        normalized_email = None
        if email:
            email_validation = AuthService.validate_email_address(email)
            if not email_validation['valid']:
                errors.append(f"Email: {email_validation['error']}")
            else:
                normalized_email = email_validation['normalized']
                # Check if email already exists
                if User.query.filter_by(email=normalized_email).first():
                    errors.append("Email already registered")
        
        # Password validation
        password_validation = AuthService.validate_password_strength(password)
        if not password_validation['valid']:
            errors.extend(password_validation['errors'])
        
        # Location validation
        if not work_location:
            errors.append("Work location is required")
        if not home_location:
            errors.append("Home location is required")
        
        # If there are errors, return them
        if errors:
            return {
                'success': False,
                'errors': errors
            }
        
        # Create new user
        try:
            hashed_password = AuthService.hash_password(password)
            
            new_user = User(
                name=name,
                phone=formatted_phone,
                email=normalized_email,
                password_hash=hashed_password,
                work_location=work_location,
                home_location=home_location
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Generate JWT token
            token = AuthService.generate_jwt_token(new_user.id)
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': new_user.to_dict(),
                'token': token
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'errors': [f'Registration failed: {str(e)}']
            }
    
    @staticmethod
    def login_user(login_data: dict) -> dict:
        """Authenticate user login"""
        from models.models import db, User  # Import here to avoid circular imports
        
        phone_or_email = login_data.get('phone_or_email', '').strip()
        password = login_data.get('password', '')
        
        if not phone_or_email or not password:
            return {
                'success': False,
                'error': 'Phone/email and password are required'
            }
        
        # Find user by phone or email
        user = None
        
        # Try to find by phone first
        if phone_or_email.startswith('+') or phone_or_email.isdigit():
            phone_validation = AuthService.validate_phone_number(phone_or_email)
            if phone_validation['valid']:
                user = User.query.filter_by(phone=phone_validation['formatted_number']).first()
        
        # If not found by phone, try email
        if not user and '@' in phone_or_email:
            email_validation = AuthService.validate_email_address(phone_or_email)
            if email_validation['valid']:
                user = User.query.filter_by(email=email_validation['normalized']).first()
        
        # Special case for admin login
        if phone_or_email == 'parthi@admin.com' and password == '7781':
            # Check if admin user exists, create if not
            if not user:
                from models.models import db
                # Check if admin exists with different phone
                existing_admin = User.query.filter_by(email='parthi@admin.com').first()
                if existing_admin:
                    user = existing_admin
                else:
                    # Use unique phone number for admin
                    admin_user = User(
                        name='Admin Parthi',
                        phone='+919876543299',  # Unique admin phone
                        email='parthi@admin.com',
                        password_hash=AuthService.hash_password('7781'),
                        work_location='Admin',
                        home_location='Admin',
                        phone_verified=True,
                        email_verified=True,
                        is_active=True
                    )
                    db.session.add(admin_user)
                    db.session.commit()
                    user = admin_user
            
            # For admin, generate token directly
            token = AuthService.generate_jwt_token(user.id)
            
            return {
                'success': True,
                'message': 'Admin login successful',
                'user': user.to_dict(),
                'token': token
            }
        
        # Regular user verification
        if not user:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        if not user.is_active:
            return {
                'success': False,
                'error': 'Account is deactivated'
            }
        
        if not AuthService.verify_password(password, user.password_hash):
            return {
                'success': False,
                'error': 'Invalid password'
            }
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = AuthService.generate_jwt_token(user.id)
        
        return {
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }
    
    @staticmethod
    def get_user_from_token(token: str) -> dict:
        """Get user information from JWT token"""
        from models.models import User  # Import here to avoid circular imports
        
        token_data = AuthService.decode_jwt_token(token)
        
        if not token_data['valid']:
            return {
                'success': False,
                'error': token_data['error']
            }
        
        user = User.query.get(token_data['user_id'])
        
        if not user or not user.is_active:
            return {
                'success': False,
                'error': 'User not found or inactive'
            }
        
        return {
            'success': True,
            'user': user.to_dict()
        }
    
    @staticmethod
    def submit_license_verification(user_id: int, license_data: dict) -> dict:
        """Submit license for verification"""
        from models.models import db, User
        
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        if not user.is_active:
            return {'success': False, 'error': 'Account is suspended or deactivated'}
        
        # Extract license data
        license_number = license_data.get('license_number', '').strip()
        license_image_url = license_data.get('license_image_url', '').strip()
        license_expiry_date = license_data.get('license_expiry_date')
        
        # Validation
        errors = []
        
        if not license_number:
            errors.append("License number is required")
        elif len(license_number) < 5:
            errors.append("License number must be at least 5 characters")
        
        # Check if license number is already used by another user
        existing_license = User.query.filter(
            User.license_number == license_number,
            User.id != user_id
        ).first()
        
        if existing_license:
            errors.append("This license number is already registered with another account")
        
        if errors:
            return {'success': False, 'errors': errors}
        
        try:
            # Parse expiry date if provided
            if license_expiry_date:
                try:
                    if isinstance(license_expiry_date, str):
                        from datetime import datetime
                        user.license_expiry_date = datetime.strptime(license_expiry_date, '%Y-%m-%d').date()
                except Exception:
                    pass
                    
            # Update user license information
            user.license_number = license_number
            user.license_image_url = license_image_url if license_image_url else None
            user.license_verification_status = 'pending'
            user.license_verified = False
            user.license_rejection_reason = None
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'License submitted for verification. Admin will review and approve/reject within 24-48 hours.',
                'verification_status': {
                    'license_submitted': True,
                    'license_verified': False,
                    'status': 'pending'
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to submit license: {str(e)}'
            }
    
    @staticmethod
    def get_verification_status(user_id: int) -> dict:
        """Get user's verification status for becoming a rider"""
        from models.models import User
        
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Check license status
        license_status = {
            'submitted': bool(user.license_number),
            'verified': user.license_verified,
            'status': user.license_verification_status,
            'rejection_reason': user.license_rejection_reason
        }
        
        # Check bike status
        verified_bikes = [bike for bike in user.bikes if bike.is_verified]
        active_bike = user.get_active_bike()
        
        bike_status = {
            'registered': len(user.bikes) > 0,
            'verified_count': len(verified_bikes),
            'has_active_verified': bool(active_bike and active_bike.is_verified),
            'pending_verification': len([bike for bike in user.bikes if not bike.is_verified])
        }
        
        # Overall rider eligibility
        can_post_rides = (
            user.license_verified and 
            active_bike and 
            active_bike.is_verified and
            user.is_active
        )
        
        # Next steps guidance
        next_steps = []
        if not license_status['submitted']:
            next_steps.append("Submit your driving license for verification")
        elif license_status['status'] == 'pending':
            next_steps.append("Wait for admin to approve your license")
        elif license_status['status'] == 'rejected':
            next_steps.append("Resubmit your license with correct documents")
        elif not bike_status['registered']:
            next_steps.append("Register your bike")
        elif bike_status['pending_verification'] > 0 and not bike_status['has_active_verified']:
            next_steps.append("Wait for admin to approve your bike registration")
        elif verified_bikes and not active_bike:
            next_steps.append("Set one of your verified bikes as active")
        elif not next_steps:
            next_steps.append("You're ready to post rides!")
        
        return {
            'success': True,
            'can_post_rides': can_post_rides,
            'license_status': license_status,
            'bike_status': bike_status,
            'next_steps': next_steps,
            'verification_progress': {
                'license_complete': license_status['verified'],
                'bike_complete': bike_status['has_active_verified'],
                'overall_complete': can_post_rides
            }
        }
    
    @staticmethod
    def update_profile(user_id: int, profile_data: dict) -> dict:
        """Update user profile information"""
        from models.models import db, User
        
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Extract profile data
        name = profile_data.get('name', '').strip()
        work_location = profile_data.get('work_location', '').strip()
        home_location = profile_data.get('home_location', '').strip()
        
        # Validation
        errors = []
        
        if name and len(name) < 2:
            errors.append("Name must be at least 2 characters long")
        
        if errors:
            return {'success': False, 'errors': errors}
        
        try:
            # Update allowed fields
            if name:
                user.name = name
            if work_location:
                user.work_location = work_location
            if home_location:
                user.home_location = home_location
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to update profile: {str(e)}'
            } 