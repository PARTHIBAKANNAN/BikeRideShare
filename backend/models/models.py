from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for riders and passengers"""
    __tablename__ = 'users'
    
    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile Information
    profile_image_url = db.Column(db.String(255), nullable=True)
    work_location = db.Column(db.String(100), nullable=False)
    home_location = db.Column(db.String(100), nullable=False)
    preferred_departure_time = db.Column(db.Time, nullable=True)
    travel_days = db.Column(db.Text, nullable=True)  # JSON: ["monday", "tuesday", ...]
    
    # Verification & Status
    phone_verified = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    
    # License Verification (Required to offer rides)
    license_number = db.Column(db.String(20), nullable=True)
    license_expiry_date = db.Column(db.Date, nullable=True)
    license_image_url = db.Column(db.String(255), nullable=True)
    license_verified = db.Column(db.Boolean, default=False)
    license_verification_status = db.Column(db.String(20), default='pending')  # pending/approved/rejected
    license_rejection_reason = db.Column(db.Text, nullable=True)
    
    # User Status & Moderation
    is_active = db.Column(db.Boolean, default=True)
    is_flagged = db.Column(db.Boolean, default=False)
    flag_reason = db.Column(db.Text, nullable=True)
    flagged_by_admin = db.Column(db.Integer, nullable=True)  # Admin user ID who flagged
    flagged_at = db.Column(db.DateTime, nullable=True)
    
    # Statistics
    rating = db.Column(db.Float, default=0.0)
    total_rides_offered = db.Column(db.Integer, default=0)
    total_rides_taken = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    bikes = db.relationship('Bike', backref='owner', lazy=True, cascade='all, delete-orphan')
    offered_rides = db.relationship('Ride', foreign_keys='Ride.rider_id', backref='rider', lazy=True)
    requested_rides = db.relationship('RideRequest', backref='passenger', lazy=True)
    
    def get_travel_days(self):
        """Get travel days as list"""
        return json.loads(self.travel_days) if self.travel_days else []
    
    def set_travel_days(self, days_list):
        """Set travel days from list"""
        self.travel_days = json.dumps(days_list)
    
    def get_active_bike(self):
        """Get currently active bike"""
        return Bike.query.filter_by(user_id=self.id, is_active=True).first()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'work_location': self.work_location,
            'home_location': self.home_location,
            'preferred_departure_time': self.preferred_departure_time.strftime('%H:%M') if self.preferred_departure_time else None,
            'travel_days': self.get_travel_days(),
            'phone_verified': self.phone_verified,
            'email_verified': self.email_verified,
            'license_number': self.license_number,
            'license_expiry_date': self.license_expiry_date.isoformat() if self.license_expiry_date else None,
            'license_image_url': self.license_image_url,
            'license_verified': self.license_verified,
            'license_verification_status': self.license_verification_status,
            'license_rejection_reason': self.license_rejection_reason,
            'rating': self.rating,
            'total_rides_offered': self.total_rides_offered,
            'total_rides_taken': self.total_rides_taken,
            'is_active': self.is_active,
            'is_flagged': self.is_flagged,
            'flag_reason': self.flag_reason,
            'flagged_at': self.flagged_at.isoformat() if self.flagged_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_active_bike(self):
        """Get the user's active bike"""
        return next((bike for bike in self.bikes if bike.is_active), None)

class Bike(db.Model):
    """Bike model for registered vehicles"""
    __tablename__ = 'bikes'
    
    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Bike Details
    bike_number = db.Column(db.String(20), unique=True, nullable=False)
    bike_type = db.Column(db.String(20), nullable=False)  # motorcycle/scooter/bike
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30), nullable=True)
    manufacture_year = db.Column(db.Integer, nullable=True)
    
    # Documents
    rc_number = db.Column(db.String(30), nullable=True)
    rc_image_url = db.Column(db.String(255), nullable=True)
    insurance_number = db.Column(db.String(50), nullable=True)
    insurance_valid_till = db.Column(db.Date, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=False)  # Only one bike can be active per user
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'bike_number': self.bike_number,
            'bike_type': self.bike_type,
            'brand': self.brand,
            'model': self.model,
            'color': self.color,
            'manufacture_year': self.manufacture_year,
            'rc_number': self.rc_number,
            'rc_image_url': self.rc_image_url,
            'insurance_number': self.insurance_number,
            'insurance_valid_till': self.insurance_valid_till.isoformat() if self.insurance_valid_till else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Ride(db.Model):
    """Ride model for offered rides"""
    __tablename__ = 'rides'
    
    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bike_id = db.Column(db.Integer, db.ForeignKey('bikes.id'), nullable=False)
    
    # Route Information
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    via_points = db.Column(db.Text, nullable=True)  # JSON: ["point1", "point2", ...]
    
    # Timing
    departure_date = db.Column(db.Date, nullable=False)
    departure_time = db.Column(db.Time, nullable=False)
    flexible_time_minutes = db.Column(db.Integer, default=15)
    
    # Ride Details
    available_seats = db.Column(db.Integer, nullable=False, default=1)
    current_passengers = db.Column(db.Integer, default=0)
    cost_per_person = db.Column(db.Float, nullable=True)
    
    # Preferences
    preferred_gender = db.Column(db.String(10), nullable=True)  # male/female/any
    additional_notes = db.Column(db.Text, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active/completed/cancelled
    is_recurring = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    bike = db.relationship('Bike', backref='rides')
    requests = db.relationship('RideRequest', backref='ride', lazy=True, cascade='all, delete-orphan')
    
    def get_via_points(self):
        """Get via points as list"""
        return json.loads(self.via_points) if self.via_points else []
    
    def set_via_points(self, points_list):
        """Set via points from list"""
        self.via_points = json.dumps(points_list)
    
    def has_available_seats(self):
        """Check if ride has available seats"""
        return self.current_passengers < self.available_seats
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        # Calculate estimated time using FareService if needed
        estimated_time = 0
        try:
            from services.fare_service import FareService
            fare_info = FareService.calculate_fare(self.from_location, self.to_location)
            estimated_time = fare_info['estimated_time_minutes']
        except:
            estimated_time = 30  # Default 30 minutes
        
        return {
            'id': self.id,
            'user_id': self.rider_id,  # Add user_id for ownership check
            'rider_id': self.rider_id,  # Add rider_id for clarity
            'rider': {
                'id': self.rider.id,
                'name': self.rider.name,
                'phone': self.rider.phone,
                'rating': self.rider.rating,
                'total_rides_offered': self.rider.total_rides_offered,
                'verified_status': {
                    'phone_verified': self.rider.phone_verified,
                    'email_verified': self.rider.email_verified
                }
            },
            'bike': {
                'bike_number': self.bike.bike_number if self.bike else 'N/A',
                'bike_type': self.bike.bike_type if self.bike else 'N/A',
                'brand': self.bike.brand if self.bike else 'N/A',
                'model': self.bike.model if self.bike else 'N/A',
                'color': self.bike.color if self.bike else 'N/A',
                'is_verified': self.bike.is_verified if self.bike else False
            },
            'route': {
                'from_location': self.from_location,
                'to_location': self.to_location,
                'via_points': self.get_via_points()
            },
            'timing': {
                'departure_date': self.departure_date.isoformat() if self.departure_date else None,
                'departure_time': self.departure_time.strftime('%H:%M') if self.departure_time else None,
                'flexible_time_minutes': self.flexible_time_minutes,
                'estimated_duration_minutes': estimated_time
            },
            'booking': {
                'available_seats': self.available_seats,
                'current_passengers': self.current_passengers,
                'cost_per_person': self.cost_per_person,
                'preferred_gender': self.preferred_gender
            },
            'details': {
                'additional_notes': self.additional_notes,
                'status': self.status,
                'is_recurring': self.is_recurring,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
        }

class RideRequest(db.Model):
    """Ride request model for passengers seeking rides or joining specific rides"""
    __tablename__ = 'ride_requests'
    
    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=True)  # Null for general requests
    
    # Route Information (for general requests)
    from_location = db.Column(db.String(100), nullable=True)
    to_location = db.Column(db.String(100), nullable=True)
    
    # Timing
    preferred_date = db.Column(db.Date, nullable=True)
    preferred_time = db.Column(db.Time, nullable=True)
    flexible_time_minutes = db.Column(db.Integer, default=30)
    
    # Request Details
    seats_needed = db.Column(db.Integer, default=1)
    max_budget = db.Column(db.Float, nullable=True)
    
    # Join Request Specific Fields
    pickup_location = db.Column(db.String(100), nullable=True)  # For specific ride joins
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending/accepted/rejected/active/matched/cancelled
    message = db.Column(db.Text, nullable=True)
    
    # Response tracking
    responded_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        base_dict = {
            'id': self.id,
            'passenger_id': self.passenger_id,
            'ride_id': self.ride_id,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
        }
        
        # Add passenger info if available
        if self.passenger:
            base_dict.update({
                'passenger_name': self.passenger.name,
                'passenger_phone': self.passenger.phone,
                'passenger_rating': getattr(self.passenger, 'rating', 0.0),
            })
        
        # Add fields based on request type
        if self.ride_id:  # Specific ride join request
            base_dict.update({
                'pickup_location': self.pickup_location,
                'seats_needed': self.seats_needed,
            })
        else:  # General ride request
            base_dict.update({
                'from_location': self.from_location,
                'to_location': self.to_location,
                'preferred_date': self.preferred_date.isoformat() if self.preferred_date else None,
                'preferred_time': self.preferred_time.isoformat() if self.preferred_time else None,
                'flexible_time_minutes': self.flexible_time_minutes,
                'seats_needed': self.seats_needed,
                'max_budget': self.max_budget,
            })
        
        return base_dict

class RideMatch(db.Model):
    """Ride match model for connecting riders and passengers"""
    __tablename__ = 'ride_matches'
    
    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('ride_requests.id'), nullable=False)
    
    # Match Details
    match_score = db.Column(db.Float, nullable=False)  # 0-100
    pickup_point = db.Column(db.String(100), nullable=True)
    drop_point = db.Column(db.String(100), nullable=True)
    estimated_additional_distance = db.Column(db.Float, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='suggested')  # suggested/accepted/rejected/completed
    rider_accepted = db.Column(db.Boolean, default=False)
    passenger_accepted = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    ride = db.relationship('Ride', backref='matches')
    request = db.relationship('RideRequest', backref='matches')
    
    def is_confirmed(self):
        """Check if match is confirmed by both parties"""
        return self.rider_accepted and self.passenger_accepted
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'ride_id': self.ride_id,
            'request_id': self.request_id,
            'match_score': self.match_score,
            'pickup_point': self.pickup_point,
            'drop_point': self.drop_point,
            'estimated_additional_distance': self.estimated_additional_distance,
            'status': self.status,
            'rider_accepted': self.rider_accepted,
            'passenger_accepted': self.passenger_accepted,
            'is_confirmed': self.is_confirmed(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Report(db.Model):
    """Report model for user complaints and issues"""
    __tablename__ = 'reports'
    
    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reported_ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=True)
    
    # Report Details
    report_type = db.Column(db.String(50), nullable=False)  # user_report, ride_report, safety_issue
    report_category = db.Column(db.String(50), nullable=False)  # harassment, no_show, safety, etc.
    description = db.Column(db.Text, nullable=False)
    evidence_urls = db.Column(db.Text, nullable=True)  # JSON array of evidence images/files
    
    # Status & Resolution
    status = db.Column(db.String(20), default='pending')  # pending, investigating, resolved, dismissed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    resolution_action = db.Column(db.String(100), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'reported_user_id': self.reported_user_id,
            'reported_ride_id': self.reported_ride_id,
            'report_type': self.report_type,
            'report_category': self.report_category,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class Notification(db.Model):
    """Notification model for ride requests and system messages"""
    __tablename__ = 'notifications'
    
    # Primary Fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification Details
    type = db.Column(db.String(50), nullable=False)  # ride_request, request_accepted, request_rejected, system
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Related Data
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=True)
    ride_request_id = db.Column(db.Integer, db.ForeignKey('ride_requests.id'), nullable=True)
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who triggered notification
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_actioned = db.Column(db.Boolean, default=False)  # For notifications requiring action
    
    # Action Data (JSON)
    action_data = db.Column(db.Text, nullable=True)  # JSON data for actions (phone numbers, etc.)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    ride = db.relationship('Ride', backref='notifications')
    ride_request = db.relationship('RideRequest', backref='notifications')
    related_user = db.relationship('User', foreign_keys=[related_user_id])

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'ride_id': self.ride_id,
            'ride_request_id': self.ride_request_id,
            'related_user_id': self.related_user_id,
            'is_read': self.is_read,
            'is_actioned': self.is_actioned,
            'action_data': json.loads(self.action_data) if self.action_data else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_actioned(self):
        """Mark notification as actioned"""
        self.is_actioned = True
        db.session.commit() 