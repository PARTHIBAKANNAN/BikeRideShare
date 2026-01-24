#!/usr/bin/env python3
"""
Notification Service for Ride Requests and Communications
"""

import json
from datetime import datetime
from models.models import db, Notification, User, Ride, RideRequest

class NotificationService:
    """Service for managing notifications and communications"""

    @staticmethod
    def create_ride_request_notification(ride_id: int, ride_request_id: int, passenger_id: int) -> dict:
        """
        Create notification for ride provider when someone requests to join their ride
        """
        try:
            # Get ride and passenger details
            ride = Ride.query.get(ride_id)
            passenger = User.query.get(passenger_id)
            ride_request = RideRequest.query.get(ride_request_id)
            
            if not ride or not passenger or not ride_request:
                return {'success': False, 'error': 'Invalid ride or passenger'}
            
            # Create notification for ride provider
            notification = Notification(
                user_id=ride.rider_id,
                type='ride_request',
                title='New Ride Request!',
                message=f'{passenger.name} wants to join your ride from {ride.from_location} to {ride.to_location}',
                ride_id=ride_id,
                ride_request_id=ride_request_id,
                related_user_id=passenger_id,
                action_data=json.dumps({
                    'passenger_name': passenger.name,
                    'passenger_phone': passenger.phone,
                    'pickup_location': ride_request.pickup_location,
                    'message': ride_request.message,
                    'seats_needed': ride_request.seats_needed
                })
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return {
                'success': True,
                'notification_id': notification.id,
                'message': 'Notification sent to ride provider'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to create notification: {str(e)}'}

    @staticmethod
    def accept_ride_request(ride_request_id: int, provider_id: int) -> dict:
        """
        Accept a ride request and create success notifications for both parties
        """
        try:
            ride_request = RideRequest.query.get(ride_request_id)
            if not ride_request:
                return {'success': False, 'error': 'Ride request not found'}
            
            ride = Ride.query.get(ride_request.ride_id)
            passenger = User.query.get(ride_request.passenger_id)
            provider = User.query.get(provider_id)
            
            if not ride or not passenger or not provider:
                return {'success': False, 'error': 'Invalid ride, passenger, or provider'}
            
            # Check if provider owns the ride
            if ride.rider_id != provider_id:
                return {'success': False, 'error': 'You can only accept requests for your own rides'}
            
            # Check available seats
            if ride.available_seats < ride_request.seats_needed:
                return {'success': False, 'error': 'Not enough seats available'}
            
            # Update ride request status
            ride_request.status = 'accepted'
            ride_request.responded_at = datetime.utcnow()
            
            # Update ride available seats
            ride.available_seats -= ride_request.seats_needed
            
            # Create success notification for passenger
            passenger_notification = Notification(
                user_id=passenger.id,
                type='request_accepted',
                title='Ride Request Accepted! 🎉',
                message=f'Great news! {provider.name} accepted your ride request. You can now contact them.',
                ride_id=ride.id,
                ride_request_id=ride_request_id,
                related_user_id=provider_id,
                action_data=json.dumps({
                    'provider_name': provider.name,
                    'provider_phone': provider.phone,
                    'ride_details': {
                        'from_location': ride.from_location,
                        'to_location': ride.to_location,
                        'departure_date': ride.departure_date.isoformat(),
                        'departure_time': ride.departure_time.strftime('%H:%M'),
                        'pickup_location': ride_request.pickup_location
                    }
                })
            )
            
            # Create confirmation notification for provider
            provider_notification = Notification(
                user_id=provider_id,
                type='request_accepted',
                title='Ride Request Confirmed ✅',
                message=f'You accepted {passenger.name}\'s request. They will contact you soon.',
                ride_id=ride.id,
                ride_request_id=ride_request_id,
                related_user_id=passenger.id,
                action_data=json.dumps({
                    'passenger_name': passenger.name,
                    'passenger_phone': passenger.phone,
                    'pickup_location': ride_request.pickup_location,
                    'seats_confirmed': ride_request.seats_needed
                })
            )
            
            db.session.add(passenger_notification)
            db.session.add(provider_notification)
            
            # Mark original request notification as actioned
            original_notification = Notification.query.filter_by(
                ride_request_id=ride_request_id,
                type='ride_request'
            ).first()
            if original_notification:
                original_notification.mark_as_actioned()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Ride request accepted successfully',
                'contact_info': {
                    'passenger_name': passenger.name,
                    'passenger_phone': passenger.phone,
                    'provider_name': provider.name,
                    'provider_phone': provider.phone
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to accept ride request: {str(e)}'}

    @staticmethod
    def reject_ride_request(ride_request_id: int, provider_id: int, reason: str = '') -> dict:
        """
        Reject a ride request and notify the passenger
        """
        try:
            ride_request = RideRequest.query.get(ride_request_id)
            if not ride_request:
                return {'success': False, 'error': 'Ride request not found'}
            
            ride = Ride.query.get(ride_request.ride_id)
            passenger = User.query.get(ride_request.passenger_id)
            provider = User.query.get(provider_id)
            
            if not ride or not passenger or not provider:
                return {'success': False, 'error': 'Invalid ride, passenger, or provider'}
            
            # Check if provider owns the ride
            if ride.rider_id != provider_id:
                return {'success': False, 'error': 'You can only reject requests for your own rides'}
            
            # Update ride request status
            ride_request.status = 'rejected'
            ride_request.responded_at = datetime.utcnow()
            
            # Create rejection notification for passenger
            rejection_message = f'Sorry, {provider.name} couldn\'t accept your ride request.'
            if reason:
                rejection_message += f' Reason: {reason}'
            rejection_message += ' Don\'t worry, keep searching for other rides!'
            
            passenger_notification = Notification(
                user_id=passenger.id,
                type='request_rejected',
                title='Ride Request Update',
                message=rejection_message,
                ride_id=ride.id,
                ride_request_id=ride_request_id,
                related_user_id=provider_id,
                action_data=json.dumps({
                    'provider_name': provider.name,
                    'rejection_reason': reason,
                    'ride_details': {
                        'from_location': ride.from_location,
                        'to_location': ride.to_location,
                        'departure_date': ride.departure_date.isoformat()
                    }
                })
            )
            
            db.session.add(passenger_notification)
            
            # Mark original request notification as actioned
            original_notification = Notification.query.filter_by(
                ride_request_id=ride_request_id,
                type='ride_request'
            ).first()
            if original_notification:
                original_notification.mark_as_actioned()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Ride request rejected'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to reject ride request: {str(e)}'}

    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False) -> dict:
        """
        Get notifications for a user
        """
        try:
            query = Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(is_read=False)
            
            notifications = query.order_by(Notification.created_at.desc()).all()
            
            return {
                'success': True,
                'notifications': [notif.to_dict() for notif in notifications],
                'unread_count': len([n for n in notifications if not n.is_read])
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get notifications: {str(e)}'}

    @staticmethod
    def mark_notification_as_read(notification_id: int, user_id: int) -> dict:
        """
        Mark a notification as read
        """
        try:
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification:
                return {'success': False, 'error': 'Notification not found'}
            
            notification.mark_as_read()
            
            return {'success': True, 'message': 'Notification marked as read'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to mark notification as read: {str(e)}'}

    @staticmethod
    def get_pending_ride_requests(provider_id: int) -> dict:
        """
        Get pending ride requests for a provider's rides
        """
        try:
            # Get provider's active rides
            provider_rides = Ride.query.filter_by(
                rider_id=provider_id,
                status='active'
            ).all()
            
            ride_ids = [ride.id for ride in provider_rides]
            
            # Get pending requests for these rides
            pending_requests = RideRequest.query.filter(
                RideRequest.ride_id.in_(ride_ids),
                RideRequest.status == 'pending'
            ).all()
            
            requests_data = []
            for req in pending_requests:
                req_dict = req.to_dict()
                # Add ride details
                ride = Ride.query.get(req.ride_id)
                if ride:
                    req_dict['ride_details'] = {
                        'from_location': ride.from_location,
                        'to_location': ride.to_location,
                        'departure_date': ride.departure_date.isoformat(),
                        'departure_time': ride.departure_time.strftime('%H:%M')
                    }
                requests_data.append(req_dict)
            
            return {
                'success': True,
                'pending_requests': requests_data,
                'count': len(requests_data)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to get pending requests: {str(e)}'} 