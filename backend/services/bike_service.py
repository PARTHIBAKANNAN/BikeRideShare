from datetime import datetime
from flask import current_app
import re
import os


class BikeService:
    """Service for bike registration, verification, and management"""
    
    @staticmethod
    def validate_bike_number(bike_number: str) -> dict:
        """Validate Indian bike registration number format"""
        # Remove spaces and convert to uppercase
        bike_number = bike_number.replace(' ', '').upper()
        
        # Indian bike number format: XX##XX#### (state code + district + letters + numbers)
        # Example: TN09AB1234, KA05MN6789
        pattern = r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'
        
        if re.match(pattern, bike_number):
            return {
                'valid': True,
                'formatted_number': bike_number,
                'state_code': bike_number[:2],
                'district_code': bike_number[2:4],
                'series': bike_number[4:-4],
                'number': bike_number[-4:]
            }
        else:
            return {
                'valid': False,
                'error': 'Invalid bike number format. Expected format: TN09AB1234'
            }
    
    @staticmethod
    def register_bike(user_id: int, bike_data: dict) -> dict:
        """Register a new bike for user"""
        from models.models import db, User, Bike
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Check if user is active
        if not user.is_active:
            return {'success': False, 'error': 'Account is suspended or deactivated'}
        
        # REQUIREMENT: User must have verified license before registering bikes
        if not user.license_verified:
            if not user.license_number:
                return {
                    'success': False, 
                    'error': 'License verification required before registering bikes. Please submit your driving license for verification first.',
                    'redirect_to': 'license_verification'
                }
            elif user.license_verification_status == 'pending':
                return {
                    'success': False, 
                    'error': 'License verification is pending admin approval. Please wait for approval before registering bikes.',
                    'redirect_to': 'verification_status'
                }
            elif user.license_verification_status == 'rejected':
                return {
                    'success': False, 
                    'error': f'License verification was rejected. Reason: {user.license_rejection_reason}. Please resubmit your license before registering bikes.',
                    'redirect_to': 'license_verification'
                }
        
        # Extract and validate bike data
        bike_number = bike_data.get('bike_number', '').strip()
        bike_type = bike_data.get('bike_type', '').strip().lower()
        brand = bike_data.get('brand', '').strip()
        model = bike_data.get('model', '').strip()
        color = bike_data.get('color', '').strip()
        manufacture_year = bike_data.get('manufacture_year')
        
        # Validation
        errors = []
        
        # Validate bike number
        bike_validation = BikeService.validate_bike_number(bike_number)
        if not bike_validation['valid']:
            errors.append(f"Bike number: {bike_validation['error']}")
        else:
            formatted_bike_number = bike_validation['formatted_number']
            # Check if bike number already exists
            existing_bike = Bike.query.filter_by(bike_number=formatted_bike_number).first()
            if existing_bike:
                errors.append("Bike number already registered")
        
        # Validate bike type
        valid_types = ['bike', 'scooter', 'motorcycle']
        if bike_type not in valid_types:
            errors.append(f"Bike type must be one of: {', '.join(valid_types)}")
        
        # Validate brand and model
        if not brand or len(brand) < 2:
            errors.append("Brand is required (minimum 2 characters)")
        if not model or len(model) < 2:
            errors.append("Model is required (minimum 2 characters)")
        
        # Validate manufacture year
        current_year = datetime.now().year
        if manufacture_year:
            try:
                year = int(manufacture_year)
                if year < 1990 or year > current_year + 1:
                    errors.append(f"Manufacture year must be between 1990 and {current_year + 1}")
            except (ValueError, TypeError):
                errors.append("Invalid manufacture year")
        
        if errors:
            return {'success': False, 'errors': errors}
        
        # Create new bike
        try:
            new_bike = Bike(
                user_id=user_id,
                bike_number=formatted_bike_number,
                bike_type=bike_type,
                brand=brand,
                model=model,
                color=color if color else None,
                manufacture_year=int(manufacture_year) if manufacture_year else None
            )
            
            db.session.add(new_bike)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Bike registered successfully. Pending admin verification.',
                'bike': new_bike.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Bike registration failed: {str(e)}'
            }
    
    @staticmethod
    def get_user_bikes(user_id: int) -> dict:
        """Get all bikes registered by user"""
        from models.models import Bike
        
        try:
            bikes = Bike.query.filter_by(user_id=user_id).all()
            return {
                'success': True,
                'bikes': [bike.to_dict() for bike in bikes],
                'total_bikes': len(bikes),
                'verified_bikes': len([b for b in bikes if b.is_verified]),
                'active_bike': next((bike.to_dict() for bike in bikes if bike.is_active), None)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to retrieve bikes: {str(e)}'
            }
    
    @staticmethod
    def set_active_bike(user_id: int, bike_id: int) -> dict:
        """Set a bike as the active bike for user"""
        from models.models import db, Bike
        
        try:
            # Get the bike to activate
            bike = Bike.query.filter_by(id=bike_id, user_id=user_id).first()
            if not bike:
                return {'success': False, 'error': 'Bike not found or not owned by user'}
            
            if not bike.is_verified:
                return {'success': False, 'error': 'Cannot activate unverified bike'}
            
            # Deactivate all other bikes for this user
            Bike.query.filter_by(user_id=user_id).update({'is_active': False})
            
            # Activate the selected bike
            bike.is_active = True
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Bike {bike.bike_number} set as active',
                'active_bike': bike.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to set active bike: {str(e)}'
            }
    
    @staticmethod
    def deactivate_bike(user_id: int, bike_id: int) -> dict:
        """Deactivate a bike (user can't post rides without an active bike)"""
        from models.models import db, Bike
        
        try:
            # Get the bike to deactivate
            bike = Bike.query.filter_by(id=bike_id, user_id=user_id, is_active=True).first()
            if not bike:
                return {'success': False, 'error': 'Active bike not found or not owned by user'}
            
            # Deactivate the bike
            bike.is_active = False
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Bike {bike.bike_number} deactivated. You can activate it again anytime.',
                'bike': bike.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to deactivate bike: {str(e)}'
            }
    
    @staticmethod
    def update_bike(user_id: int, bike_id: int, update_data: dict) -> dict:
        """Update bike information"""
        from models.models import db, Bike
        
        try:
            bike = Bike.query.filter_by(id=bike_id, user_id=user_id).first()
            if not bike:
                return {'success': False, 'error': 'Bike not found or not owned by user'}
            
            # Only allow updating certain fields
            allowed_fields = ['color', 'insurance_expiry', 'rc_expiry']
            
            for field in allowed_fields:
                if field in update_data:
                    if field.endswith('_expiry') and update_data[field]:
                        try:
                            # Parse date string to datetime
                            expiry_date = datetime.strptime(update_data[field], '%Y-%m-%d').date()
                            setattr(bike, field, expiry_date)
                        except ValueError:
                            return {'success': False, 'error': f'Invalid date format for {field}. Use YYYY-MM-DD'}
                    else:
                        setattr(bike, field, update_data[field])
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Bike updated successfully',
                'bike': bike.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to update bike: {str(e)}'
            }
    
    @staticmethod
    def delete_bike(user_id: int, bike_id: int) -> dict:
        """Delete a bike (only if not verified or has no active rides)"""
        from models.models import db, Bike
        
        try:
            bike = Bike.query.filter_by(id=bike_id, user_id=user_id).first()
            if not bike:
                return {'success': False, 'error': 'Bike not found or not owned by user'}
            
            # Check if bike has active rides (when ride model is implemented)
            # For now, only allow deletion of unverified bikes
            if bike.is_verified:
                return {
                    'success': False, 
                    'error': 'Cannot delete verified bike. Please contact admin.'
                }
            
            db.session.delete(bike)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Bike {bike.bike_number} deleted successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to delete bike: {str(e)}'
            }
    
    @staticmethod
    def verify_bike_documents(bike_data: dict) -> dict:
        """Validate bike documents (RC, Insurance) - for admin use"""
        errors = []
        
        rc_number = bike_data.get('rc_number', '').strip()
        insurance_number = bike_data.get('insurance_number', '').strip()
        rc_expiry = bike_data.get('rc_expiry')
        insurance_expiry = bike_data.get('insurance_expiry')
        
        # RC validation
        if not rc_number:
            errors.append("RC number is required")
        
        # Insurance validation
        if not insurance_number:
            errors.append("Insurance number is required")
        
        # Date validations
        today = datetime.now().date()
        
        if rc_expiry:
            try:
                rc_date = datetime.strptime(rc_expiry, '%Y-%m-%d').date()
                if rc_date <= today:
                    errors.append("RC is expired")
            except ValueError:
                errors.append("Invalid RC expiry date format")
        
        if insurance_expiry:
            try:
                insurance_date = datetime.strptime(insurance_expiry, '%Y-%m-%d').date()
                if insurance_date <= today:
                    errors.append("Insurance is expired")
            except ValueError:
                errors.append("Invalid insurance expiry date format")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def get_bike_stats() -> dict:
        """Get bike statistics for admin dashboard"""
        from models.models import Bike
        
        try:
            total_bikes = Bike.query.count()
            verified_bikes = Bike.query.filter_by(is_verified=True).count()
            pending_bikes = Bike.query.filter_by(is_verified=False).count()
            active_bikes = Bike.query.filter_by(is_active=True).count()
            
            # Group by bike type
            bike_types = {}
            for bike_type in ['bike', 'scooter', 'motorcycle']:
                count = Bike.query.filter_by(bike_type=bike_type).count()
                bike_types[bike_type] = count
            
            return {
                'success': True,
                'stats': {
                    'total_bikes': total_bikes,
                    'verified_bikes': verified_bikes,
                    'pending_verification': pending_bikes,
                    'active_bikes': active_bikes,
                    'by_type': bike_types
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get bike stats: {str(e)}'
            } 