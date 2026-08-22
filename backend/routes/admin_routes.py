from flask import request, jsonify
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.admin_service import AdminService
from datetime import datetime

# Create admin namespace
admin_ns = Namespace('admin', description='Admin operations', security='Bearer')

# Define models for request/response documentation
admin_stats_model = admin_ns.model('AdminStats', {
    'total_users': fields.Integer(description='Total users'),
    'active_users': fields.Integer(description='Active users'),
    'total_bikes': fields.Integer(description='Total bikes'),
    'total_rides': fields.Integer(description='Total rides')
})

license_verification_model = admin_ns.model('LicenseVerification', {
    'user_id': fields.Integer(description='User ID'),
    'action': fields.String(description='approve or reject'),
    'rejection_reason': fields.String(description='Reason for rejection (if rejecting)')
})

user_action_model = admin_ns.model('UserAction', {
    'user_id': fields.Integer(description='User ID'),
    'reason': fields.String(description='Reason for action')
})

bike_verification_model = admin_ns.model('BikeVerification', {
    'bike_id': fields.Integer(description='Bike ID'),
    'action': fields.String(description='approve or reject')
})

report_resolution_model = admin_ns.model('ReportResolution', {
    'report_id': fields.Integer(description='Report ID'),
    'resolution_action': fields.String(description='Action taken'),
    'admin_notes': fields.String(description='Admin notes')
})

@admin_ns.route('/check-access')
class CheckAdminAccess(Resource):
    @admin_ns.doc('check_admin_access', security='Bearer')
    @jwt_required()
    def get(self):
        """Check if current user has admin access"""
        try:
            current_user_id = get_jwt_identity()
            has_access = AdminService.verify_admin_access(current_user_id)
            
            return {
                'success': True,
                'has_admin_access': has_access,
                'user_id': str(current_user_id)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to check admin access: {str(e)}'
            }, 500

@admin_ns.route('/dashboard')
class AdminDashboard(Resource):
    @admin_ns.doc('get_admin_dashboard', security='Bearer')
    @jwt_required()
    def get(self):
        """Get admin dashboard data"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            # Get platform statistics
            stats_result = AdminService.get_platform_stats()
            
            # Get pending verifications
            pending_licenses = AdminService.get_pending_license_verifications()
            pending_bikes = AdminService.get_pending_bike_verifications()
            
            # Get recent reports
            recent_reports = AdminService.get_all_reports(status='pending')
            
            return {
                'success': True,
                'platform_stats': stats_result.get('platform_stats', {}),
                'pending_verifications': {
                    'licenses': pending_licenses.get('pending_verifications', [])[:5],
                    'bikes': pending_bikes.get('pending_bikes', [])[:5]
                },
                'recent_reports': recent_reports.get('reports', [])[:5],
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get admin dashboard: {str(e)}'
            }, 500

# LICENSE VERIFICATION ROUTES
@admin_ns.route('/license-verifications')
class LicenseVerifications(Resource):
    @admin_ns.doc('get_pending_license_verifications', security='Bearer')
    @jwt_required()
    def get(self):
        """Get all pending license verifications"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            result = AdminService.get_pending_license_verifications()
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get pending license verifications: {str(e)}'
            }, 500

@admin_ns.route('/license-verifications/verify')
class VerifyLicense(Resource):
    @admin_ns.doc('verify_user_license', security='Bearer')
    @admin_ns.expect(license_verification_model)
    @jwt_required()
    def post(self):
        """Approve or reject a user's license verification"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            data = request.json
            user_id = data.get('user_id')
            action = data.get('action')
            rejection_reason = data.get('rejection_reason')
            
            if not user_id or not action:
                return {'success': False, 'error': 'user_id and action are required'}, 400
            
            result = AdminService.verify_user_license(current_user_id, user_id, action, rejection_reason)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to verify license: {str(e)}'
            }, 500

# USER MANAGEMENT ROUTES
@admin_ns.route('/users')
class AllUsers(Resource):
    @admin_ns.doc('get_all_users', security='Bearer')
    @jwt_required()
    def get(self):
        """Get all users with pagination and filtering"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            search = request.args.get('search', None)
            filter_flagged = request.args.get('flagged', None)
            
            if filter_flagged is not None:
                filter_flagged = filter_flagged.lower() == 'true'
            
            result = AdminService.get_all_users(page, per_page, search, filter_flagged)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get users: {str(e)}'
            }, 500

@admin_ns.route('/users/<int:user_id>')
class UserDetails(Resource):
    @admin_ns.doc('get_user_details', security='Bearer')
    @jwt_required()
    def get(self, user_id):
        """Get detailed information about a specific user"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            result = AdminService.get_user_details(user_id)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get user details: {str(e)}'
            }, 500

@admin_ns.route('/users/flag')
class FlagUser(Resource):
    @admin_ns.doc('flag_user', security='Bearer')
    @admin_ns.expect(user_action_model)
    @jwt_required()
    def post(self):
        """Flag a user for misconduct"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            data = request.json
            user_id = data.get('user_id')
            reason = data.get('reason')
            
            if not user_id or not reason:
                return {'success': False, 'error': 'user_id and reason are required'}, 400
            
            result = AdminService.flag_user(current_user_id, user_id, reason)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to flag user: {str(e)}'
            }, 500

@admin_ns.route('/users/unflag')
class UnflagUser(Resource):
    @admin_ns.doc('unflag_user', security='Bearer')
    @admin_ns.expect(user_action_model)
    @jwt_required()
    def post(self):
        """Remove flag from a user"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            data = request.json
            user_id = data.get('user_id')
            
            if not user_id:
                return {'success': False, 'error': 'user_id is required'}, 400
            
            result = AdminService.unflag_user(current_user_id, user_id)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to unflag user: {str(e)}'
            }, 500

@admin_ns.route('/users/suspend')
class SuspendUser(Resource):
    @admin_ns.doc('suspend_user', security='Bearer')
    @admin_ns.expect(user_action_model)
    @jwt_required()
    def post(self):
        """Suspend a user account"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            data = request.json
            user_id = data.get('user_id')
            reason = data.get('reason')
            
            if not user_id or not reason:
                return {'success': False, 'error': 'user_id and reason are required'}, 400
            
            result = AdminService.suspend_user(current_user_id, user_id, reason)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to suspend user: {str(e)}'
            }, 500

@admin_ns.route('/users/reactivate')
class ReactivateUser(Resource):
    @admin_ns.doc('reactivate_user', security='Bearer')
    @admin_ns.expect(user_action_model)
    @jwt_required()
    def post(self):
        """Reactivate a suspended user"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            data = request.json
            user_id = data.get('user_id')
            
            if not user_id:
                return {'success': False, 'error': 'user_id is required'}, 400
            
            result = AdminService.reactivate_user(current_user_id, user_id)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to reactivate user: {str(e)}'
            }, 500

# BIKE VERIFICATION ROUTES
@admin_ns.route('/bike-verifications')
class BikeVerifications(Resource):
    @admin_ns.doc('get_pending_bike_verifications', security='Bearer')
    @jwt_required()
    def get(self):
        """Get all pending bike verifications"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            result = AdminService.get_pending_bike_verifications()
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get pending bike verifications: {str(e)}'
            }, 500

@admin_ns.route('/bike-verifications/verify')
class VerifyBikeRegistration(Resource):
    @admin_ns.doc('verify_bike_registration', security='Bearer')
    @admin_ns.expect(bike_verification_model)
    @jwt_required()
    def post(self):
        """Approve or reject a bike registration"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            data = request.json
            bike_id = data.get('bike_id')
            action = data.get('action')
            rejection_reason = data.get('rejection_reason')
            
            if not bike_id or not action:
                return {'success': False, 'error': 'bike_id and action are required'}, 400
            
            result = AdminService.verify_bike_registration(current_user_id, bike_id, action, rejection_reason)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to verify bike: {str(e)}'
            }, 500

# REPORT MANAGEMENT ROUTES
@admin_ns.route('/reports')
class AllReports(Resource):
    @admin_ns.doc('get_all_reports', security='Bearer')
    @jwt_required()
    def get(self):
        """Get all reports with optional filtering"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            status = request.args.get('status', None)
            priority = request.args.get('priority', None)
            
            result = AdminService.get_all_reports(status, priority)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get reports: {str(e)}'
            }, 500

@admin_ns.route('/reports/<int:report_id>/assign')
class AssignReport(Resource):
    @admin_ns.doc('assign_report', security='Bearer')
    @jwt_required()
    def post(self, report_id):
        """Assign a report to current admin"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            result = AdminService.assign_report(current_user_id, report_id)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to assign report: {str(e)}'
            }, 500

@admin_ns.route('/reports/resolve')
class ResolveReport(Resource):
    @admin_ns.doc('resolve_report', security='Bearer')
    @admin_ns.expect(report_resolution_model)
    @jwt_required()
    def post(self):
        """Resolve a report with action taken"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            data = request.json
            report_id = data.get('report_id')
            resolution_action = data.get('resolution_action')
            admin_notes = data.get('admin_notes')
            
            if not report_id or not resolution_action:
                return {'success': False, 'error': 'report_id and resolution_action are required'}, 400
            
            result = AdminService.resolve_report(current_user_id, report_id, resolution_action, admin_notes)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to resolve report: {str(e)}'
            }, 500

# RIDE MANAGEMENT ROUTES
@admin_ns.route('/rides')
class AllRides(Resource):
    @admin_ns.doc('get_all_rides', security='Bearer')
    @jwt_required()
    def get(self):
        """Get all rides with pagination and filtering"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            status = request.args.get('status', None)
            
            result = AdminService.get_all_rides(page, per_page, status)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get rides: {str(e)}'
            }, 500

# LEGACY ROUTES (keeping for compatibility)
@admin_ns.route('/platform-stats')
class PlatformStats(Resource):
    @admin_ns.doc('get_platform_statistics', security='Bearer')
    @jwt_required()
    def get(self):
        """Get platform statistics"""
        try:
            current_user_id = get_jwt_identity()
            
            if not AdminService.verify_admin_access(current_user_id):
                return {'success': False, 'error': 'Admin access required'}, 403
            
            result = AdminService.get_platform_stats()
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get platform stats: {str(e)}'
            }, 500

@admin_ns.route('/incident-reports')
class AdminIncidentReports(Resource):
    @admin_ns.doc('get_admin_incident_reports', security='Bearer')
    @jwt_required()
    def get(self):
        """Get all commuter/rider incident reports"""
        current_user_id = get_jwt_identity()
        if not AdminService.verify_admin_access(current_user_id):
            return {'success': False, 'error': 'Admin access required'}, 403
        status = request.args.get('status')
        return AdminService.get_incident_reports(status), 200

@admin_ns.route('/incident-reports/<int:report_id>/action')
class AdminIncidentReportAction(Resource):
    @admin_ns.doc('action_admin_incident_report', security='Bearer')
    @jwt_required()
    def post(self, report_id):
        """Take moderation action on an incident report"""
        current_user_id = get_jwt_identity()
        if not AdminService.verify_admin_access(current_user_id):
            return {'success': False, 'error': 'Admin access required'}, 403
        data = request.get_json() or {}
        action = data.get('action', 'action_taken')
        notes = data.get('notes', '')
        return AdminService.action_incident_report(report_id, action, notes), 200

@admin_ns.route('/bikes-directory')
class AdminBikesDirectory(Resource):
    @admin_ns.doc('get_all_bikes_directory', security='Bearer')
    @jwt_required()
    def get(self):
        """Get all registered vehicles and owners across the platform"""
        current_user_id = get_jwt_identity()
        if not AdminService.verify_admin_access(current_user_id):
            return {'success': False, 'error': 'Admin access required'}, 403
        return AdminService.get_all_platform_bikes(), 200

@admin_ns.route('/users/<int:user_id>/blacklist')
class AdminBlacklistUser(Resource):
    @admin_ns.doc('blacklist_user', security='Bearer')
    @jwt_required()
    def post(self, user_id):
        """Blacklist and suspend a user account"""
        current_user_id = get_jwt_identity()
        if not AdminService.verify_admin_access(current_user_id):
            return {'success': False, 'error': 'Admin access required'}, 403
        data = request.get_json() or {}
        reason = data.get('reason', 'Policy violation')
        return AdminService.blacklist_user(user_id, reason), 200

@admin_ns.route('/users/<int:user_id>/unblacklist')
class AdminUnblacklistUser(Resource):
    @admin_ns.doc('unblacklist_user', security='Bearer')
    @jwt_required()
    def post(self, user_id):
        """Reinstate a suspended user account"""
        current_user_id = get_jwt_identity()
        if not AdminService.verify_admin_access(current_user_id):
            return {'success': False, 'error': 'Admin access required'}, 403
        return AdminService.unblacklist_user(user_id), 200

@admin_ns.route('/bikes/<int:bike_id>/blacklist')
class AdminBlacklistBike(Resource):
    @admin_ns.doc('blacklist_bike', security='Bearer')
    @jwt_required()
    def post(self, bike_id):
        """Blacklist and ban a vehicle plate number"""
        current_user_id = get_jwt_identity()
        if not AdminService.verify_admin_access(current_user_id):
            return {'success': False, 'error': 'Admin access required'}, 403
        data = request.get_json() or {}
        reason = data.get('reason', 'Unsafe vehicle or document fraud')
        return AdminService.blacklist_bike(bike_id, reason), 200 