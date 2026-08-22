from datetime import datetime, time
from typing import Dict, Any
from services.route_service import RouteService


class FareService:
    """Service for calculating fair ride-share pricing based on real Chennai road distances"""
    
    # Base fare configuration (Bike pooling friendly rates)
    BASE_RATE_PER_KM = 5.0  # Rs 5 per km
    PEAK_TIME_MULTIPLIER = 1.35  # 35% surcharge during peak office rush hours
    LONG_DISTANCE_THRESHOLD = 15.0  # km
    LONG_DISTANCE_DISCOUNT = 0.85  # 15% discount for long distances (> 15km)
    MIN_FARE = 25.0  # Minimum fare Rs 25
    
    # Peak time slots (Chennai Office Commute Hours)
    MORNING_PEAK_START = time(8, 0)   # 8:00 AM
    MORNING_PEAK_END = time(10, 30)   # 10:30 AM
    EVENING_PEAK_START = time(17, 0)  # 5:00 PM
    EVENING_PEAK_END = time(20, 30)   # 8:30 PM
    
    @staticmethod
    def calculate_distance(from_location: str, to_location: str) -> float:
        """Calculate real driving road distance using RouteService"""
        try:
            route_info = RouteService.calculate_road_route(from_location, to_location)
            return float(route_info.get('distance_km', 10.0))
        except Exception as e:
            print(f"⚠️ Route calculation error in FareService: {e}")
            return 10.0
    
    @staticmethod
    def is_peak_time(departure_time) -> bool:
        """Check if the given time falls in peak office commute hours"""
        if isinstance(departure_time, str):
            try:
                # Handle HH:MM or HH:MM:SS
                parts = departure_time.split(':')
                departure_time = time(int(parts[0]), int(parts[1]))
            except Exception:
                return False
        elif not isinstance(departure_time, time):
            return False
        
        # Check morning and evening peak
        if FareService.MORNING_PEAK_START <= departure_time <= FareService.MORNING_PEAK_END:
            return True
        if FareService.EVENING_PEAK_START <= departure_time <= FareService.EVENING_PEAK_END:
            return True
        
        return False
    
    @staticmethod
    def calculate_fare(from_location: str, to_location: str, departure_time=None, bike_type='bike') -> Dict[str, Any]:
        """Calculate fair commute price breakdown based on real road distance"""
        route_info = RouteService.calculate_road_route(from_location, to_location)
        distance_km = float(route_info.get('distance_km', 10.0))
        estimated_duration = int(route_info.get('duration_minutes', 25))
        
        # Base fare calculation
        base_fare = distance_km * FareService.BASE_RATE_PER_KM
        
        # Apply peak time surcharge if applicable
        peak_surcharge = 0.0
        is_peak = False
        if departure_time:
            is_peak = FareService.is_peak_time(departure_time)
            if is_peak:
                peak_surcharge = base_fare * (FareService.PEAK_TIME_MULTIPLIER - 1.0)
        
        # Apply long distance discount if applicable (> 15 km)
        long_distance_discount = 0.0
        if distance_km > FareService.LONG_DISTANCE_THRESHOLD:
            subtotal = base_fare + peak_surcharge
            long_distance_discount = subtotal * (1.0 - FareService.LONG_DISTANCE_DISCOUNT)
        
        # Final fare before vehicle multiplier
        final_fare = base_fare + peak_surcharge - long_distance_discount
        final_fare = max(final_fare, FareService.MIN_FARE)
        
        # Bike type adjustment
        bike_multiplier = 1.0
        b_type = (bike_type or 'bike').lower()
        if 'motorcycle' in b_type or 'bullet' in b_type or 'cruiser' in b_type:
            bike_multiplier = 1.15  # 15% more for premium cruiser/motorcycle
        elif 'scooter' in b_type or 'activa' in b_type or 'jupiter' in b_type or 'ev' in b_type:
            bike_multiplier = 0.95  # 5% economical for scooters/EVs
        
        final_fare = max(round(final_fare * bike_multiplier), int(FareService.MIN_FARE))
        
        return {
            'distance_km': distance_km,
            'base_fare': round(base_fare, 2),
            'peak_surcharge': round(peak_surcharge, 2) if peak_surcharge > 0 else 0,
            'long_distance_discount': round(long_distance_discount, 2) if long_distance_discount > 0 else 0,
            'bike_type_multiplier': bike_multiplier,
            'final_fare': int(final_fare),
            'is_peak_time': is_peak,
            'estimated_time_minutes': estimated_duration,
            'coordinates': route_info.get('coordinates', []),
            'breakdown': {
                'base_rate_per_km': FareService.BASE_RATE_PER_KM,
                'total_distance': distance_km,
                'peak_time_applied': is_peak,
                'long_distance_discount_applied': distance_km > FareService.LONG_DISTANCE_THRESHOLD,
                'minimum_fare_applied': final_fare == FareService.MIN_FARE
            }
        }
    
    @staticmethod
    def get_fare_estimate(from_location: str, to_location: str, departure_time=None) -> Dict[str, Any]:
        """Get quick fare estimate with coordinates for route planning"""
        fare_info = FareService.calculate_fare(from_location, to_location, departure_time)
        return {
            'from_location': from_location,
            'to_location': to_location,
            'distance_km': fare_info['distance_km'],
            'estimated_fare': fare_info['final_fare'],
            'estimated_time_minutes': fare_info['estimated_time_minutes'],
            'is_peak_time': fare_info['is_peak_time'],
            'coordinates': fare_info.get('coordinates', [])
        }