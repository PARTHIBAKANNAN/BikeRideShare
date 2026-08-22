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
                is_recurring=is_recurring
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
            
            # Use AI-powered intelligent matching
            matched_rides = ai_route_matcher.find_intelligent_matches(search_request, available_rides)
            
            # Determine search type based on AI configuration
            search_type = 'ai_intelligent' if ai_route_matcher.is_configured else 'basic_enhanced'
            
            return {
                'success': True,
                'rides': matched_rides,
                'total_rides': len(matched_rides),
                'search_criteria': {
                    'from_location': from_location,
                    'to_location': to_location,
                    'travel_date': travel_date,
                    'seats_needed': seats_needed_val,
                    'max_cost': max_cost
                },
                'search_type': search_type,
                'ai_powered': ai_route_matcher.is_configured,
                'message': RideService._get_search_message(matched_rides, search_type, from_location, to_location)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to search rides: {str(e)}'
            }
    
    @staticmethod
    def _get_search_message(matched_rides: list, search_type: str, from_location: str, to_location: str) -> str:
        """Generate helpful search result message"""
        
        if not matched_rides:
            if search_type == 'ai_intelligent':
                return f"No suitable rides found for {from_location} to {to_location}. AI analyzed all available routes including via points and nearby options."
            else:
                return f"No rides found for {from_location} to {to_location}. Try expanding your search criteria or check different dates."
        
        if search_type == 'ai_intelligent':
            high_score_rides = len([r for r in matched_rides if r.get('ai_match_score', 0) >= 80])
            if high_score_rides > 0:
                return f"Found {len(matched_rides)} intelligent matches! {high_score_rides} rides have excellent route compatibility."
            else:
                return f"Found {len(matched_rides)} potential matches with route analysis. Check AI recommendations for best options."
        else:
            return f"Found {len(matched_rides)} rides. Results enhanced with basic route analysis."
    
    @staticmethod
    def request_ride_join(user_id: int, ride_id: int, request_data: dict) -> dict:
        """Request to join a specific ride"""
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