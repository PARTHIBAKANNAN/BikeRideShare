#!/usr/bin/env python3
"""
Notification API Routes for Ride Sharing App
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.notification_service import NotificationService
from services.ride_service import RideService

# Create namespace
notification_ns = Namespace('notifications', description='Notification operations', security='Bearer')

# Swagger models
notification_model = notification_ns.model('Notification', {
    'id': fields.Integer(description='Notification ID'),
    'type': fields.String(description='Notification type'),
    'title': fields.String(description='Notification title'),
    'message': fields.String(description='Notification message'),
    'is_read': fields.Boolean(description='Read status'),
    'created_at': fields.String(description='Creation timestamp')
})

accept_request_model = notification_ns.model('AcceptRequest', {
    'ride_request_id': fields.Integer(required=True, description='Ride request ID to accept')
})

reject_request_model = notification_ns.model('RejectRequest', {
    'ride_request_id': fields.Integer(required=True, description='Ride request ID to reject'),
    'reason': fields.String(description='Rejection reason')
})

@notification_ns.route('/notifications')
class UserNotifications(Resource):
    @notification_ns.doc('get_user_notifications')
    @notification_ns.param('unread_only', 'Get only unread notifications', type='boolean', default=False)
    @notification_ns.response(200, 'Notifications retrieved', fields.List(fields.Nested(notification_model)))
    @jwt_required()
    def get(self):
        """Get user notifications"""
        user_id = get_jwt_identity()
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        result = NotificationService.get_user_notifications(user_id, unread_only)
        
        if result['success']:
            return {
                'success': True,
                'notifications': result['notifications'],
                'unread_count': result['unread_count']
            }, 200
        else:
            return {'success': False, 'error': result['error']}, 400

@notification_ns.route('/notifications/<int:notification_id>/read')
class MarkNotificationRead(Resource):
    @notification_ns.doc('mark_notification_read')
    @notification_ns.response(200, 'Notification marked as read')
    @jwt_required()
    def post(self, notification_id):
        """Mark notification as read"""
        user_id = get_jwt_identity()
        
        result = NotificationService.mark_notification_as_read(notification_id, user_id)
        
        if result['success']:
            return {'success': True, 'message': result['message']}, 200
        else:
            return {'success': False, 'error': result['error']}, 400

@notification_ns.route('/ride-requests/pending')
class PendingRideRequests(Resource):
    @notification_ns.doc('get_pending_ride_requests')
    @notification_ns.response(200, 'Pending ride requests retrieved')
    @jwt_required()
    def get(self):
        """Get pending ride requests for provider's rides"""
        provider_id = get_jwt_identity()
        
        result = RideService.get_ride_requests_for_my_rides(provider_id)
        
        if result['success']:
            return {
                'success': True,
                'pending_requests': result['pending_requests'],
                'count': result['count']
            }, 200
        else:
            return {'success': False, 'error': result['error']}, 400

@notification_ns.route('/ride-requests/accept')
class AcceptRideRequest(Resource):
    @notification_ns.doc('accept_ride_request')
    @notification_ns.expect(accept_request_model)
    @notification_ns.response(200, 'Ride request accepted')
    @jwt_required()
    def post(self):
        """Accept a ride request (provider action)"""
        provider_id = get_jwt_identity()
        data = request.get_json()
        
        ride_request_id = data.get('ride_request_id')
        if not ride_request_id:
            return {'success': False, 'error': 'Ride request ID is required'}, 400
        
        result = RideService.accept_ride_request(ride_request_id, provider_id)
        
        if result['success']:
            return {
                'success': True,
                'message': result['message'],
                'contact_info': result.get('contact_info')
            }, 200
        else:
            return {'success': False, 'error': result['error']}, 400

@notification_ns.route('/ride-requests/reject')
class RejectRideRequest(Resource):
    @notification_ns.doc('reject_ride_request')
    @notification_ns.expect(reject_request_model)
    @notification_ns.response(200, 'Ride request rejected')
    @jwt_required()
    def post(self):
        """Reject a ride request (provider action)"""
        provider_id = get_jwt_identity()
        data = request.get_json()
        
        ride_request_id = data.get('ride_request_id')
        reason = data.get('reason', '')
        
        if not ride_request_id:
            return {'success': False, 'error': 'Ride request ID is required'}, 400
        
        result = RideService.reject_ride_request(provider_id, ride_request_id, reason)
        
        if result['success']:
            return {'success': True, 'message': result['message']}, 200
        else:
            return {'success': False, 'error': result['error']}, 400

@notification_ns.route('/my-requests')
class MyRideRequests(Resource):
    @notification_ns.doc('get_my_ride_requests')
    @notification_ns.response(200, 'My ride requests retrieved')
    @jwt_required()
    def get(self):
        """Get ride requests made by user (as passenger)"""
        user_id = get_jwt_identity()
        
        result = RideService.get_my_ride_requests(user_id)
        
        if result['success']:
            return {
                'success': True,
                'requests': result['requests'],
                'total_requests': result['total_requests']
            }, 200
        else:
            return {'success': False, 'error': result['error']}, 400 