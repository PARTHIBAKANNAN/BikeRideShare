from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models.models import db, User, Bike, Ride, RideRequest, RideMatch, Report


class AdminService:
    """Service for admin-only operations and management"""
    
    ADMIN_EMAIL = "admin@gmail.com"
    ADMIN_PASS = "Admin@7781"
    
    @staticmethod
    def verify_admin_access(user_id: int) -> bool:
        """Check if user has admin access"""
        from models.models import User
        
        user = User.query.get(user_id)
        if not user:
            return False
        
        return user.email.lower() == AdminService.ADMIN_EMAIL.lower()
    
    @staticmethod
    def verify_admin_credentials(email: str, password: str) -> bool:
        """Verify admin credentials directly"""
        return email.lower() == AdminService.ADMIN_EMAIL.lower() and password == AdminService.ADMIN_PASS
    
    @staticmethod
    def get_platform_stats() -> dict:
        """Get comprehensive platform statistics"""
        try:
            # User statistics
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            flagged_users = User.query.filter_by(is_flagged=True).count()
            verified_phone_users = User.query.filter_by(phone_verified=True).count()
            verified_email_users = User.query.filter_by(email_verified=True).count()
            license_verified_users = User.query.filter_by(license_verified=True).count()
            
            # Bike statistics
            total_bikes = Bike.query.count()
            verified_bikes = Bike.query.filter_by(is_verified=True).count()
            active_bikes = Bike.query.filter_by(is_active=True).count()
            
            # Ride statistics
            total_rides = Ride.query.count()
            active_rides = Ride.query.filter_by(status='active').count()
            completed_rides = Ride.query.filter_by(status='completed').count()
            
            # Request statistics
            total_requests = RideRequest.query.count()
            pending_requests = RideRequest.query.filter_by(status='pending').count()
            
            # Report statistics
            total_reports = Report.query.count()
            pending_reports = Report.query.filter_by(status='pending').count()
            resolved_reports = Report.query.filter_by(status='resolved').count()
            
            # Pending approvals
            pending_license_verifications = User.query.filter_by(license_verification_status='pending').count()
            pending_bike_verifications = Bike.query.filter_by(is_verified=False).count()
            
            return {
                'success': True,
                'platform_stats': {
                    'users': {
                        'total': total_users,
                        'active': active_users,
                        'flagged': flagged_users,
                        'phone_verified': verified_phone_users,
                        'email_verified': verified_email_users,
                        'license_verified': license_verified_users
                    },
                    'bikes': {
                        'total': total_bikes,
                        'verified': verified_bikes,
                        'active': active_bikes
                    },
                    'rides': {
                        'total': total_rides,
                        'active': active_rides,
                        'completed': completed_rides
                    },
                    'requests': {
                        'total': total_requests,
                        'pending': pending_requests
                    },
                    'reports': {
                        'total': total_reports,
                        'pending': pending_reports,
                        'resolved': resolved_reports
                    },
                    'pending_approvals': {
                        'license_verifications': pending_license_verifications,
                        'bike_verifications': pending_bike_verifications
                    }
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get platform stats: {str(e)}'
            }

    # LICENSE VERIFICATION METHODS
    @staticmethod
    def get_pending_license_verifications() -> dict:
        """Get users with pending license verifications"""
        try:
            pending_users = User.query.filter_by(license_verification_status='pending').filter(
                User.license_number.isnot(None)
            ).all()
            
            return {
                'success': True,
                'pending_verifications': [
                    {
                        'user_id': user.id,
                        'name': user.name,
                        'phone': user.phone,
                        'email': user.email,
                        'license_number': user.license_number,
                        'license_image_url': user.license_image_url,
                        'created_at': user.created_at.isoformat() if user.created_at else None
                    } for user in pending_users
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get pending license verifications: {str(e)}'
            }

    @staticmethod
    def verify_user_license(admin_id: int, user_id: int, action: str, rejection_reason: str = None) -> dict:
        """Approve or reject user license verification"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            if action == 'approve':
                user.license_verified = True
                user.license_verification_status = 'approved'
                user.license_rejection_reason = None
                message = f'License verified for user {user.name}'
            elif action == 'reject':
                user.license_verified = False
                user.license_verification_status = 'rejected'
                user.license_rejection_reason = rejection_reason or 'License verification failed'
                message = f'License rejected for user {user.name}'
            else:
                return {'success': False, 'error': 'Invalid action. Use approve or reject'}
            
            db.session.commit()
            
            return {
                'success': True,
                'message': message,
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to verify license: {str(e)}'
            }

    # USER MANAGEMENT METHODS
    @staticmethod
    def flag_user(admin_id: int, user_id: int, reason: str) -> dict:
        """Flag a user for misconduct"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            user.is_flagged = True
            user.flag_reason = reason
            user.flagged_by_admin = admin_id
            user.flagged_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'User {user.name} has been flagged',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to flag user: {str(e)}'
            }

    @staticmethod
    def unflag_user(admin_id: int, user_id: int) -> dict:
        """Remove flag from a user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            user.is_flagged = False
            user.flag_reason = None
            user.flagged_by_admin = None
            user.flagged_at = None
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'User {user.name} has been unflagged',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to unflag user: {str(e)}'
            }

    @staticmethod
    def suspend_user(admin_id: int, user_id: int, reason: str) -> dict:
        """Suspend a user account"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            user.is_active = False
            user.is_flagged = True
            user.flag_reason = f'SUSPENDED: {reason}'
            user.flagged_by_admin = admin_id
            user.flagged_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'User {user.name} has been suspended',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to suspend user: {str(e)}'
            }

    @staticmethod
    def reactivate_user(admin_id: int, user_id: int) -> dict:
        """Reactivate a suspended user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            user.is_active = True
            user.is_flagged = False
            user.flag_reason = None
            user.flagged_by_admin = None
            user.flagged_at = None
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'User {user.name} has been reactivated',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to reactivate user: {str(e)}'
            }

    # BIKE VERIFICATION METHODS  
    @staticmethod
    def get_pending_bike_verifications() -> dict:
        """Get bikes pending verification"""
        try:
            pending_bikes = Bike.query.filter_by(is_verified=False).join(User).all()
            
            return {
                'success': True,
                'pending_bikes': [
                    {
                        'bike_id': bike.id,
                        'owner': {
                            'id': bike.owner.id,
                            'name': bike.owner.name,
                            'phone': bike.owner.phone
                        },
                        'bike_number': bike.bike_number,
                        'bike_type': bike.bike_type,
                        'brand': bike.brand,
                        'model': bike.model,
                        'manufacture_year': bike.manufacture_year,
                        'rc_number': bike.rc_number,
                        'insurance_valid_till': bike.insurance_valid_till.isoformat() if bike.insurance_valid_till else None,
                        'created_at': bike.created_at.isoformat() if bike.created_at else None
                    } for bike in pending_bikes
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get pending bike verifications: {str(e)}'
            }

    @staticmethod
    def verify_bike_registration(admin_id: int, bike_id: int, action: str) -> dict:
        """Approve or reject bike verification"""
        try:
            bike = Bike.query.get(bike_id)
            if not bike:
                return {'success': False, 'error': 'Bike not found'}
            
            if action == 'approve':
                bike.is_verified = True
                
                # Auto-activate logic: If user has no other active bikes, make this one active
                user_active_bikes = Bike.query.filter_by(
                    user_id=bike.user_id, 
                    is_active=True
                ).count()
                
                if user_active_bikes == 0:
                    bike.is_active = True
                    message = f'Bike {bike.bike_number} verified and set as active bike'
                else:
                    message = f'Bike {bike.bike_number} verified successfully. You can set it as active in bike management.'
                    
            elif action == 'reject':
                # Remove unverified bike
                db.session.delete(bike)
                message = f'Bike {bike.bike_number} verification rejected and removed'
            else:
                return {'success': False, 'error': 'Invalid action. Use approve or reject'}
            
            db.session.commit()
            
            return {
                'success': True,
                'message': message,
                'bike': bike.to_dict() if action == 'approve' else None
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to verify bike: {str(e)}'
            }

    # REPORT MANAGEMENT METHODS
    @staticmethod
    def get_all_reports(status: str = None, priority: str = None) -> dict:
        """Get all reports with optional filtering"""
        try:
            query = Report.query
            
            if status:
                query = query.filter_by(status=status)
            if priority:
                query = query.filter_by(priority=priority)
            
            reports = query.order_by(Report.created_at.desc()).all()
            
            return {
                'success': True,
                'reports': [report.to_dict() for report in reports],
                'total_reports': len(reports)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get reports: {str(e)}'
            }

    @staticmethod
    def assign_report(admin_id: int, report_id: int) -> dict:
        """Assign a report to an admin"""
        try:
            report = Report.query.get(report_id)
            if not report:
                return {'success': False, 'error': 'Report not found'}
            
            report.assigned_admin_id = admin_id
            report.status = 'under_review'
            report.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Report assigned successfully',
                'report': report.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to assign report: {str(e)}'
            }

    @staticmethod
    def resolve_report(admin_id: int, report_id: int, resolution_action: str, admin_notes: str) -> dict:
        """Resolve a report with action taken"""
        try:
            report = Report.query.get(report_id)
            if not report:
                return {'success': False, 'error': 'Report not found'}
            
            report.status = 'resolved'
            report.resolution_action = resolution_action
            report.admin_notes = admin_notes
            report.resolved_at = datetime.utcnow()
            report.updated_at = datetime.utcnow()
            
            # Take action based on resolution
            if resolution_action in ['suspend', 'flag'] and report.reported_user_id:
                if resolution_action == 'suspend':
                    AdminService.suspend_user(admin_id, report.reported_user_id, f"Report #{report.id}: {report.description[:100]}")
                elif resolution_action == 'flag':
                    AdminService.flag_user(admin_id, report.reported_user_id, f"Report #{report.id}: {report.description[:100]}")
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Report resolved successfully',
                'report': report.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to resolve report: {str(e)}'
            }

    # GENERAL ADMIN METHODS
    @staticmethod
    def get_all_users(page: int = 1, per_page: int = 50, search: str = None, filter_flagged: bool = None) -> dict:
        """Get all users with pagination and filtering"""
        try:
            query = User.query
            
            if search:
                query = query.filter(
                    or_(
                        User.name.contains(search),
                        User.phone.contains(search),
                        User.email.contains(search)
                    )
                )
            
            if filter_flagged is not None:
                query = query.filter_by(is_flagged=filter_flagged)
            
            users = query.order_by(User.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'success': True,
                'users': [user.to_dict() for user in users.items],
                'pagination': {
                    'total': users.total,
                    'pages': users.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': users.has_next,
                    'has_prev': users.has_prev
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get users: {str(e)}'
            }

    @staticmethod
    def get_all_rides(page: int = 1, per_page: int = 50, status: str = None) -> dict:
        """Get all rides with pagination and filtering"""
        try:
            query = Ride.query
            
            if status:
                query = query.filter_by(status=status)
            
            rides = query.order_by(Ride.created_at.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'success': True,
                'rides': [ride.to_dict() for ride in rides.items],
                'pagination': {
                    'total': rides.total,
                    'pages': rides.pages,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': rides.has_next,
                    'has_prev': rides.has_prev
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get rides: {str(e)}'
            }

    @staticmethod
    def get_user_details(user_id: int) -> dict:
        """Get detailed information about a specific user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Get user's bikes
            bikes = Bike.query.filter_by(user_id=user_id).all()
            
            # Get user's rides
            rides = Ride.query.filter_by(rider_id=user_id).limit(10).all()
            
            # Get user's reports (both filed and received)
            filed_reports = Report.query.filter_by(reporter_id=user_id).limit(10).all()
            received_reports = Report.query.filter_by(reported_user_id=user_id).limit(10).all()
            
            return {
                'success': True,
                'user': user.to_dict(),
                'bikes': [bike.to_dict() for bike in bikes],
                'recent_rides': [ride.to_dict() for ride in rides],
                'filed_reports': [report.to_dict() for report in filed_reports],
                'received_reports': [report.to_dict() for report in received_reports]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get user details: {str(e)}'
            } 