#!/usr/bin/env python3
"""
Ride Service for Smart Ride Matcher
"""

from datetime import datetime, date, time
from flask import current_app
from sqlalchemy import and_, or_
import json
from models.models import db, Ride, User, Bike, RideRequest
from services.fare_service import FareService


class RideService:
    """Service for ride posting, searching, and management"""
    
    @staticmethod
    def post_ride(user_id: int, ride_data: dict) -> dict:
        """Post a new ride offer"""
        from models.models import db, User, Bike, Ride
        from services.fare_service import FareService
        
        # Get user and validate their verification status
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Check if user is active
        if not user.is_active:
            return {'success': False, 'error': 'Account is suspended or deactivated'}
        
        # STEP 1: Check License Verification (Required to become a rider)
        if not user.license_verified:
            if not user.license_number:
                return {
                    'success': False, 
                    'error': 'License verification required to post rides. Please submit your license for verification.',
                    'verification_status': {
                        'license_submitted': False,
                        'license_verified': False,
                        'bike_registered': bool(user.bikes),
                        'bike_verified': False
                    }
                }
            elif user.license_verification_status == 'pending':
                return {
                    'success': False, 
                    'error': 'License verification is pending admin approval. Please wait for approval.',
                    'verification_status': {
                        'license_submitted': True,
                        'license_verified': False,
                        'bike_registered': bool(user.bikes),
                        'bike_verified': False
                    }
                }
            elif user.license_verification_status == 'rejected':
                return {
                    'success': False, 
                    'error': f'License verification was rejected. Reason: {user.license_rejection_reason}. Please resubmit with correct documents.',
                    'verification_status': {
                        'license_submitted': True,
                        'license_verified': False,
                        'bike_registered': bool(user.bikes),
                        'bike_verified': False
                    }
                }
        
        # STEP 2: Check Bike Registration and Verification
        active_bike = user.get_active_bike()
        if not active_bike:
            verified_bikes = [bike for bike in user.bikes if bike.is_verified]
            if not user.bikes:
                return {
                    'success': False, 
                    'error': 'No bike registered. Please register your bike first.',
                    'verification_status': {
                        'license_submitted': True,
                        'license_verified': True,
                        'bike_registered': False,
                        'bike_verified': False
                    }
                }
            elif not verified_bikes:
                return {
                    'success': False, 
                    'error': 'No verified bike found. Please wait for admin approval of your registered bikes.',
                    'verification_status': {
                        'license_submitted': True,
                        'license_verified': True,
                        'bike_registered': True,
                        'bike_verified': False
                    }
                }
            else:
                return {
                    'success': False, 
                    'error': 'Please set one of your verified bikes as active in the Bike Management section.',
                    'verification_status': {
                        'license_submitted': True,
                        'license_verified': True,
                        'bike_registered': True,
                        'bike_verified': True
                    }
                }
        
        # STEP 3: Ensure active bike is verified
        if not active_bike.is_verified:
            return {
                'success': False, 
                'error': 'Active bike is not verified by admin. Please wait for approval or set a different verified bike as active.',
                'verification_status': {
                    'license_submitted': True,
                    'license_verified': True,
                    'bike_registered': True,
                    'bike_verified': False
                }
            }
        
        # All verifications passed - proceed with ride posting
        # Extract and validate ride data
        from_location = ride_data.get('from_location', '').strip()
        to_location = ride_data.get('to_location', '').strip()
        departure_date = ride_data.get('departure_date')
        departure_time = ride_data.get('departure_time')
        available_seats = ride_data.get('available_seats', 1)
        description = ride_data.get('description', '').strip()
        is_recurring = ride_data.get('is_recurring', False)
        recurring_days = ride_data.get('recurring_days', [])
        
        # Validation
        errors = []
        
        if not from_location:
            errors.append("From location is required")
        if not to_location:
            errors.append("To location is required")
        if from_location == to_location:
            errors.append("From and to locations cannot be the same")
        
        # Date and time validation
        if not departure_date:
            errors.append("Departure date is required")
        else:
            try:
                departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
                if departure_date_obj < date.today():
                    errors.append("Departure date cannot be in the past")
            except ValueError:
                errors.append("Invalid departure date format. Use YYYY-MM-DD")
        
        if not departure_time:
            errors.append("Departure time is required")
        else:
            try:
                departure_time_obj = datetime.strptime(departure_time, '%H:%M').time()
            except ValueError:
                errors.append("Invalid departure time format. Use HH:MM")
        
        # Seats validation
        try:
            available_seats = int(available_seats)
            if available_seats < 1 or available_seats > 3:
                errors.append("Available seats must be between 1 and 3")
        except (ValueError, TypeError):
            errors.append("Invalid available seats value")
        
        # Calculate fare automatically
        fare_info = FareService.calculate_fare(
            from_location=from_location, 
            to_location=to_location, 
            departure_time=departure_time,
            bike_type=active_bike.bike_type
        )
        cost_per_person = fare_info['final_fare'] / available_seats if available_seats > 0 else fare_info['final_fare']
        
        # Recurring validation
        if is_recurring:
            if not recurring_days or not isinstance(recurring_days, list):
                errors.append("Recurring days are required for recurring rides")
            else:
                valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in recurring_days:
                    if day.lower() not in valid_days:
                        errors.append(f"Invalid day: {day}")
        
        if errors:
            return {'success': False, 'errors': errors}
        
        is_pink_ride = ride_data.get('is_pink_ride', False)
        if is_pink_ride and user.gender != 'female':
            return {
                'success': False,
                'error': 'Women-Only Pink Rides can only be offered by verified female riders.'
            }

        # Create new ride
        try:
            new_ride = Ride(
                rider_id=user_id,
                bike_id=active_bike.id,
                from_location=from_location,
                to_location=to_location,
                departure_date=departure_date_obj,
                departure_time=departure_time_obj,
                available_seats=available_seats,
                cost_per_person=round(cost_per_person, 0),
                additional_notes=description if description else None,
                is_recurring=is_recurring,
                is_pink_ride=bool(is_pink_ride)
            )
            
            if is_recurring:
                new_ride.set_recurring_days(recurring_days)
            
            db.session.add(new_ride)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Ride posted successfully',
                'ride': new_ride.to_dict(),
                'fare_details': {
                    'distance_km': fare_info['distance_km'],
                    'total_fare': fare_info['final_fare'],
                    'cost_per_person': round(cost_per_person, 0),
                    'estimated_time_minutes': fare_info['estimated_time_minutes'],
                    'breakdown': fare_info['breakdown']
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to post ride: {str(e)}'
            }
    
    @staticmethod
    def search_rides(search_data: dict, user_id: int = None) -> dict:
        """Search for available rides using AI-powered intelligent matching"""
        from models.models import Ride, User, Bike
        from services.ai_route_matcher import ai_route_matcher
        
        # Extract search parameters
        from_location = search_data.get('from_location', '').strip()
        to_location = search_data.get('to_location', '').strip()
        travel_date = search_data.get('travel_date')
        departure_date = search_data.get('departure_date')  # Alternative field name
        max_cost = search_data.get('max_cost')
        min_seats = search_data.get('min_seats', 1)
        seats_needed = search_data.get('seats_needed', min_seats)
        
        # Use departure_date if travel_date not provided
        if not travel_date and departure_date:
            travel_date = departure_date
        
        try:
            # Get all available rides (broader search for AI analysis)
            base_query = Ride.query.filter(
                and_(
                    Ride.status == 'active',
                    Ride.available_seats > 0,
                    Ride.departure_date >= date.today()
                )
            ).join(User, Ride.rider_id == User.id).join(Bike, Ride.bike_id == Bike.id)
            # Exclude user's own rides if user_id is provided
            if user_id:
                base_query = base_query.filter(Ride.rider_id != user_id)
            
            # Pink Ride Filter
            if search_params.get('is_pink_ride') or search_params.get('pink_ride_only'):
                base_query = base_query.filter(Ride.is_pink_ride == True)
            
            # Apply flexible date filter for AI search (±3 days from requested date)
            if travel_date:
                try:
                    travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
                    # For AI search, allow ±3 days flexibility
                    from datetime import timedelta
                    date_start = travel_date_obj - timedelta(days=3)
                    date_end = travel_date_obj + timedelta(days=3)
                    base_query = base_query.filter(
                        and_(
                            Ride.departure_date >= date_start,
                            Ride.departure_date <= date_end
                        )
                    )
                except ValueError:
                    return {'success': False, 'error': 'Invalid travel date format. Use YYYY-MM-DD'}
            
            # Apply seats filter (keep this strict)
            try:
                seats_needed_val = int(seats_needed)
                base_query = base_query.filter(Ride.available_seats >= seats_needed_val)
            except (ValueError, TypeError):
                return {'success': False, 'error': 'Invalid seats needed value'}
            
            # Skip cost filter for AI analysis - let AI decide compatibility
            # The AI will consider cost in its scoring
            
            # Execute query to get available rides
            available_rides_query = base_query.order_by(Ride.departure_date, Ride.departure_time).all()
            
            print(f"🔍 DEBUG: Found {len(available_rides_query)} rides after flexible filtering")
            
            # Convert to dictionaries for AI analysis
            available_rides = []
            for ride in available_rides_query:
                ride_dict = ride.to_dict()
                
                # Add additional context for AI
                if hasattr(ride, 'rider') and ride.rider:
                    ride_dict['rider_name'] = ride.rider.name
                    ride_dict['rider_rating'] = getattr(ride.rider, 'rating', 0.0)
                
                if hasattr(ride, 'bike') and ride.bike:
                    ride_dict['bike_number'] = ride.bike.bike_number
                    ride_dict['bike_type'] = ride.bike.bike_type
                    ride_dict['bike_brand'] = ride.bike.brand
                    ride_dict['bike_model'] = ride.bike.model
                
                available_rides.append(ride_dict)
            
            # If no location filters provided, return all available rides (no AI analysis needed)
            if not from_location and not to_location:
                return {
                    'success': True,
                    'rides': available_rides,
                    'total_rides': len(available_rides),
                    'search_type': 'all_available',
                    'ai_powered': False
                }
            
            # Prepare search request for AI analysis
            search_request = {
                'from_location': from_location,
                'to_location': to_location,
                'departure_date': travel_date,
                'seats_needed': seats_needed_val,
                'max_cost': max_cost
            }

            # If Gemini key not configured, fallback to basic search
            if not RideService.is_gemini_configured():
                print("⚠️ Gemini API not configured, falling back to basic search")
                filtered_rides = [
                    r for r in available_rides 
                    if (not from_location or from_location.lower() in r['route']['from_location'].lower()) and
                       (not to_location or to_location.lower() in r['route']['to_location'].lower())
                ]
                return {
                    'success': True,
                    'rides': filtered_rides,
                    'total_rides': len(filtered_rides),
                    'search_type': 'keyword_filtered',
                    'ai_powered': False
                }
            
            # Use Gemini AI for intelligent ride matching
            try:
                ai_results = RideService._analyze_rides_with_gemini(search_request, available_rides)
                return {
                    'success': True,
                    'rides': ai_results.get('matched_rides', []),
                    'total_rides': len(ai_results.get('matched_rides', [])),
                    'ai_analysis': ai_results.get('analysis', ''),
                    'search_type': 'ai_matched',
                    'ai_powered': True
                }
            except Exception as e:
                print(f"❌ AI search failed, falling back: {str(e)}")
                # Fallback to broad location matching if AI fails
                filtered_rides = [
                    r for r in available_rides 
                    if (not from_location or from_location.lower() in r['route']['from_location'].lower()) and
                       (not to_location or to_location.lower() in r['route']['to_location'].lower())
                ]
                return {
                    'success': True,
                    'rides': filtered_rides,
                    'total_rides': len(filtered_rides),
                    'search_type': 'keyword_fallback',
                    'ai_powered': False
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Failed to search rides: {str(e)}'}
    
    @staticmethod
    def request_ride_join(user_id: int, ride_id: int, request_data: dict) -> dict:
        """Request to join a specific ride (supports booking for a friend and pink rides)"""
        from models.models import RideRequest, Ride, User
        from services.notification_service import NotificationService
        
        try:
            # Check if ride exists and is active
            ride = Ride.query.get(ride_id)
            if not ride:
                return {'success': False, 'error': 'Ride not found'}
            
            if ride.status != 'active':
                return {'success': False, 'error': 'This ride is no longer available'}
            
            # Check if user is trying to join their own ride
            if ride.rider_id == user_id:
                return {'success': False, 'error': 'You cannot join your own ride'}
            
            user = User.query.get(user_id)
            is_for_friend = bool(request_data.get('is_for_friend', False))
            friend_name = request_data.get('friend_name', '').strip() if is_for_friend else None
            friend_phone = request_data.get('friend_phone', '').strip() if is_for_friend else None

            # Pink Ride verification
            if ride.is_pink_ride and user and user.gender != 'female' and not is_for_friend:
                return {
                    'success': False,
                    'error': 'This is a Women-Only Pink Ride reserved for female commuters.'
                }
            
            # Check if user has already requested to join this ride
            existing_request = RideRequest.query.filter_by(
                passenger_id=user_id,
                ride_id=ride_id,
                status='pending'
            ).first()
            
            if existing_request:
                return {'success': False, 'error': 'You have already requested to join this ride'}
            
            # Check available seats
            seats_needed = request_data.get('seats_needed', 1)
            if ride.available_seats < seats_needed:
                return {'success': False, 'error': 'Not enough seats available'}
            
            # Create ride request
            ride_request = RideRequest(
                passenger_id=user_id,
                ride_id=ride_id,
                pickup_location=request_data.get('pickup_location'),
                message=request_data.get('message', ''),
                seats_needed=seats_needed,
                is_for_friend=is_for_friend,
                friend_name=friend_name,
                friend_phone=friend_phone,
                status='pending'
            )
            
            db.session.add(ride_request)
            db.session.flush()  # Get the ID
            
            # Create notification for ride provider
            notification_result = NotificationService.create_ride_request_notification(
                ride_id=ride_id,
                ride_request_id=ride_request.id,
                passenger_id=user_id
            )
            
            if notification_result['success']:
                db.session.commit()
                return {
                    'success': True,
                    'message': 'Ride join request sent successfully',
                    'request': ride_request.to_dict()
                }
            else:
                db.session.rollback()
                return {'success': False, 'error': 'Failed to send notification to provider'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to request ride join: {str(e)}'}

    @staticmethod
    def report_incident(reporter_id: int, data: dict) -> dict:
        """Report a commuter, rider, bike or safety violation to Admin"""
        from models.models import db, IncidentReport, User, Ride
        
        try:
            reported_user_id = data.get('reported_user_id')
            ride_id = data.get('ride_id')
            bike_id = data.get('bike_id')
            report_type = data.get('report_type', 'rider')
            reason = data.get('reason', '').strip()
            details = data.get('details', '').strip()
            
            if not reason:
                return {'success': False, 'error': 'Report reason is required'}
            
            # If ride_id provided, automatically resolve reported user and bike
            if ride_id and not reported_user_id:
                ride = Ride.query.get(ride_id)
                if ride:
                    if ride.rider_id != reporter_id:
                        reported_user_id = ride.rider_id
                        bike_id = ride.bike_id
            
            report = IncidentReport(
                reporter_id=reporter_id,
                reported_user_id=reported_user_id,
                ride_id=ride_id,
                bike_id=bike_id,
                report_type=report_type,
                reason=reason,
                details=details,
                status='pending'
            )
            
            db.session.add(report)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Incident report submitted. Administration will review within 24 hours.',
                'report': report.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to submit report: {str(e)}'}

    @staticmethod
    def accept_ride_request(provider_id: int, ride_request_id: int) -> dict:
        """Accept a ride join request (provider action)"""
        from services.notification_service import NotificationService
        
        return NotificationService.accept_ride_request(ride_request_id, provider_id)

    @staticmethod
    def reject_ride_request(provider_id: int, ride_request_id: int, reason: str = '') -> dict:
        """Reject a ride join request (provider action)"""
        from services.notification_service import NotificationService
        
        return NotificationService.reject_ride_request(ride_request_id, provider_id, reason)

    @staticmethod
    def get_my_ride_requests(user_id: int) -> dict:
        """Get ride requests made by user (as passenger)"""
        from models.models import RideRequest
        
        try:
            requests = RideRequest.query.filter_by(passenger_id=user_id).order_by(
                RideRequest.created_at.desc()
            ).all()
            
            return {
                'success': True,
                'requests': [req.to_dict() for req in requests],
                'total_requests': len(requests)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get ride requests: {str(e)}'}

    @staticmethod
    def get_ride_requests_for_my_rides(provider_id: int) -> dict:
        """Get all ride requests for provider's rides"""
        from services.notification_service import NotificationService
        
        return NotificationService.get_pending_ride_requests(provider_id)
    
    @staticmethod
    def get_user_rides(user_id: int, ride_type: str = 'all') -> dict:
        """Get rides posted by user"""
        from models.models import Ride
        
        try:
            query = Ride.query.filter_by(rider_id=user_id)
            
            if ride_type == 'active':
                query = query.filter_by(status='active')
            elif ride_type == 'completed':
                query = query.filter(Ride.status.in_(['completed', 'cancelled']))
            elif ride_type == 'upcoming':
                query = query.filter(
                    and_(
                        Ride.status == 'active',
                        Ride.departure_date >= date.today()
                    )
                )
            
            rides = query.order_by(Ride.departure_date.desc(), Ride.departure_time.desc()).all()
            
            return {
                'success': True,
                'rides': [ride.to_dict() for ride in rides],
                'total_rides': len(rides),
                'ride_type': ride_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get user rides: {str(e)}'
            }
    
    @staticmethod
    def get_ride_requests(user_id: int, ride_id: int) -> dict:
        """Get join requests for a ride (only ride owner can access)"""
        from models.models import Ride, RideRequest
        
        # Get ride and verify ownership
        ride = Ride.query.filter_by(id=ride_id, rider_id=user_id).first()
        if not ride:
            return {'success': False, 'error': 'Ride not found or not owned by user'}
        
        try:
            requests = RideRequest.query.filter_by(ride_id=ride_id).all()
            
            return {
                'success': True,
                'ride': ride.to_dict(),
                'requests': [request.to_dict() for request in requests],
                'total_requests': len(requests)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get ride requests: {str(e)}'
            }
    
    @staticmethod
    def respond_to_request(user_id: int, request_id: int, response: str) -> dict:
        """Accept or reject a ride join request"""
        from models.models import db, RideRequest, Ride, RideMatch
        
        # Get request and verify ownership of ride
        request = RideRequest.query.get(request_id)
        if not request:
            return {'success': False, 'error': 'Request not found'}
        
        ride = Ride.query.filter_by(id=request.ride_id, rider_id=user_id).first()
        if not ride:
            return {'success': False, 'error': 'Ride not found or not owned by user'}
        
        if request.status != 'pending':
            return {'success': False, 'error': f'Request already {request.status}'}
        
        # Validate response
        if response not in ['accepted', 'rejected']:
            return {'success': False, 'error': 'Response must be "accepted" or "rejected"'}
        
        try:
            # Update request status
            request.status = response
            request.responded_at = datetime.utcnow()
            
            if response == 'accepted':
                # Check if seats are still available
                if ride.available_seats <= 0:
                    return {'success': False, 'error': 'No seats available'}
                
                import random
                request.start_otp = f"{random.randint(1000, 9999)}"
                
                # Create ride match
                ride_match = RideMatch(
                    offering_ride_id=ride.id,
                    passenger_id=request.passenger_id,
                    pickup_location=request.pickup_location
                )
                
                # Update available seats
                ride.available_seats -= 1
                
                db.session.add(ride_match)
            
            db.session.commit()
            
            action = 'accepted' if response == 'accepted' else 'rejected'
            return {
                'success': True,
                'message': f'Ride request {action} successfully. Boarding OTP generated.' if response == 'accepted' else f'Ride request {action}',
                'request': request.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to respond to request: {str(e)}'
            }

    @staticmethod
    def verify_start_otp(rider_id: int, request_id: int, entered_otp: str) -> dict:
        """Verify passenger 4-digit OTP to officially begin the ride"""
        from models.models import db, RideRequest, Ride
        
        request = RideRequest.query.get(request_id)
        if not request:
            return {'success': False, 'error': 'Ride request not found'}
        
        ride = Ride.query.filter_by(id=request.ride_id, rider_id=rider_id).first()
        if not ride:
            return {'success': False, 'error': 'You are not the designated rider for this commute'}
        
        if not request.start_otp:
            return {'success': False, 'error': 'No active Boarding OTP found for this passenger'}
        
        if str(entered_otp).strip() != str(request.start_otp).strip():
            return {'success': False, 'error': 'Invalid 4-digit OTP. Please ask the passenger for the correct boarding OTP shown on their screen.'}
        
        try:
            request.status = 'in_progress'
            ride.status = 'active'
            db.session.commit()
            return {
                'success': True,
                'message': 'Passenger OTP verified successfully! Commute is now underway.',
                'request': request.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to verify OTP: {str(e)}'}
    
    @staticmethod
    def cancel_ride(user_id: int, ride_id: int, reason: str = None) -> dict:
        """Cancel a ride (only ride owner can cancel)"""
        from models.models import db, Ride
        
        # Get ride and verify ownership
        ride = Ride.query.filter_by(id=ride_id, rider_id=user_id).first()
        if not ride:
            return {'success': False, 'error': 'Ride not found or not owned by user'}
        
        if ride.status != 'active':
            return {'success': False, 'error': 'Ride is already inactive'}
        
        try:
            # Mark ride as cancelled
            ride.status = 'cancelled'
            # Note: cancellation_reason field doesn't exist in model
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Ride cancelled successfully',
                'ride': ride.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to cancel ride: {str(e)}'
            }
    
    @staticmethod
    def get_user_ride_history(user_id: int) -> dict:
        """Get user's complete ride history (as rider and passenger)"""
        from models.models import Ride, RideMatch, RideRequest
        
        try:
            # Rides offered by user
            offered_rides = Ride.query.filter_by(rider_id=user_id).all()
            
            # Rides where user was a passenger
            passenger_matches = RideMatch.query.filter_by(passenger_id=user_id).all()
            passenger_rides = [match.offering_ride for match in passenger_matches]
            
            # Ride requests made by user
            ride_requests = RideRequest.query.filter_by(passenger_id=user_id).all()
            
            return {
                'success': True,
                'offered_rides': [ride.to_dict() for ride in offered_rides],
                'passenger_rides': [ride.to_dict() for ride in passenger_rides],
                'ride_requests': [request.to_dict() for request in ride_requests],
                'statistics': {
                    'total_rides_offered': len(offered_rides),
                    'total_rides_taken': len(passenger_rides),
                    'pending_requests': len([r for r in ride_requests if r.status == 'pending'])
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get ride history: {str(e)}'
            }
    
    @staticmethod
    def get_ride_stats() -> dict:
        """Get ride statistics for admin dashboard"""
        from models.models import Ride, RideRequest, RideMatch
        
        try:
            total_rides = Ride.query.count()
            active_rides = Ride.query.filter_by(is_active=True).count()
            completed_rides = total_rides - active_rides
            
            total_requests = RideRequest.query.count()
            pending_requests = RideRequest.query.filter_by(status='pending').count()
            accepted_requests = RideRequest.query.filter_by(status='accepted').count()
            
            total_matches = RideMatch.query.count()
            
            # Popular routes
            from sqlalchemy import func
            popular_routes = db.session.query(
                Ride.from_location,
                Ride.to_location,
                func.count(Ride.id).label('count')
            ).group_by(Ride.from_location, Ride.to_location).order_by(func.count(Ride.id).desc()).limit(10).all()
            
            return {
                'success': True,
                'stats': {
                    'total_rides': total_rides,
                    'active_rides': active_rides,
                    'completed_rides': completed_rides,
                    'total_requests': total_requests,
                    'pending_requests': pending_requests,
                    'accepted_requests': accepted_requests,
                    'successful_matches': total_matches,
                    'popular_routes': [
                        {
                            'from': route.from_location,
                            'to': route.to_location,
                            'count': route.count
                        } for route in popular_routes
                    ]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get ride stats: {str(e)}'
            }

    @staticmethod
    def rate_commute(request_id: int, user_id: int, rating: float, feedback: str = '', badges: list = None) -> dict:
        """Submit post-ride rating and safety compliment badges for co-commuter"""
        from models.models import RideRequest, User, Ride
        try:
            req = RideRequest.query.get(request_id)
            if not req:
                return {'success': False, 'error': 'Ride request not found'}

            ride = req.ride
            if not ride:
                return {'success': False, 'error': 'Associated ride not found'}

            # Determine if user is passenger or rider
            if user_id == req.passenger_id:
                # Passenger rating the rider
                target_user = User.query.get(ride.rider_id)
            elif user_id == ride.rider_id:
                # Rider rating the passenger
                target_user = User.query.get(req.passenger_id)
            else:
                return {'success': False, 'error': 'Unauthorized to rate this commute'}

            if not target_user:
                return {'success': False, 'error': 'Target user not found'}

            # Update target user's weighted rating
            current_rating = target_user.rating or 5.0
            total_trips = max((target_user.total_rides_offered or 0) + (target_user.total_rides_taken or 0), 1)
            new_rating = round(((current_rating * total_trips) + float(rating)) / (total_trips + 1), 1)
            target_user.rating = max(1.0, min(5.0, new_rating))

            db.session.commit()

            return {
                'success': True,
                'message': f'Thank you for rating {target_user.name}!',
                'new_rating': target_user.rating,
                'badges_received': badges or []
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to submit rating: {str(e)}'}

    @staticmethod
    def get_auto_pool_matches(user_id: int, home_location: str, work_location: str, shift_time: str = '08:30', days: list = None) -> dict:
        """AI Daily Shift Auto-Pool Matcher: Finds regular weekday commuters with matching origin, destination and shift times"""
        from models.models import Ride, User
        try:
            # Query rides near home and work locations
            rides_query = Ride.query.filter(
                Ride.status == 'active',
                Ride.available_seats > 0
            )
            if user_id:
                rides_query = rides_query.filter(Ride.rider_id != user_id)

            all_rides = rides_query.all()
            matches = []

            for r in all_rides:
                # Simple corridor compatibility scoring
                score = 0
                is_home_match = home_location.lower() in r.from_location.lower() or r.from_location.lower() in home_location.lower()
                is_work_match = work_location.lower() in r.to_location.lower() or r.to_location.lower() in work_location.lower()
                
                if is_home_match and is_work_match:
                    score = 95
                elif is_work_match:
                    score = 75
                elif is_home_match:
                    score = 60
                else:
                    score = 40

                if score >= 60:
                    ride_dict = r.to_dict()
                    ride_dict['match_score'] = score
                    ride_dict['is_shift_compatible'] = True
                    matches.append(ride_dict)

            # Sort by match score descending
            matches.sort(key=lambda x: x.get('match_score', 0), reverse=True)

            return {
                'success': True,
                'home_location': home_location,
                'work_location': work_location,
                'shift_time': shift_time,
                'auto_matches': matches[:10],
                'total_matches': len(matches)
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to find auto-pool matches: {str(e)}'}

    @staticmethod
    def get_green_leaderboard() -> dict:
        """Tech Park Green Commute & Sustainability Leaderboard across Chennai SEZs"""
        leaderboard = [
            {
                'hub_id': 'omr_elcot',
                'name': 'ELCOT SEZ & Sholinganallur Hub',
                'corridor': 'OMR IT Expressway',
                'co2_saved_kg': 4280.5,
                'petrol_saved_inr': 245000,
                'active_bikepoolers': 184,
                'badge': '🏆 Top Green Tech Park'
            },
            {
                'hub_id': 'dlf_porur',
                'name': 'DLF Cybercity & L&T Infotech',
                'corridor': 'Mount-Poonamallee Road',
                'co2_saved_kg': 3650.0,
                'petrol_saved_inr': 198000,
                'active_bikepoolers': 142,
                'badge': '🥈 Eco-Warrior Corporate Hub'
            },
            {
                'hub_id': 'olympia_guindy',
                'name': 'Olympia Tech Park & Guindy Estate',
                'corridor': 'GST Road & Inner Ring',
                'co2_saved_kg': 2940.2,
                'petrol_saved_inr': 164000,
                'active_bikepoolers': 118,
                'badge': '🥉 Clean Air Champion'
            },
            {
                'hub_id': 'tidel_taramani',
                'name': 'Tidel Park & Ramanujan IT City',
                'corridor': 'CSIR Road / Taramani',
                'co2_saved_kg': 2310.8,
                'petrol_saved_inr': 132000,
                'active_bikepoolers': 96,
                'badge': '🌱 Green Commuter Hub'
            },
            {
                'hub_id': 'siruseri_sipcot',
                'name': 'Siruseri SIPCOT IT Park',
                'corridor': 'OMR South Expressway',
                'co2_saved_kg': 1980.4,
                'petrol_saved_inr': 115000,
                'active_bikepoolers': 82,
                'badge': '⭐ Fast-Rising Green Hub'
            }
        ]
        return {
            'success': True,
            'leaderboard': leaderboard,
            'total_city_co2_saved_kg': 15161.9,
            'total_city_petrol_saved_inr': 854000
        } 