from datetime import datetime, time
import json


class FareService:
    """Service for calculating ride fares"""
    
    # Base fare configuration
    BASE_RATE_PER_KM = 5.0  # Rs 5 per km
    PEAK_TIME_MULTIPLIER = 1.5  # 50% surcharge during peak hours
    LONG_DISTANCE_THRESHOLD = 15  # km
    LONG_DISTANCE_DISCOUNT = 0.85  # 15% discount for rides > 15km
    MIN_FARE = 25.0  # Minimum fare Rs 25
    
    # Peak time slots (in 24-hour format)
    MORNING_PEAK_START = time(8, 0)   # 8:00 AM
    MORNING_PEAK_END = time(10, 0)    # 10:00 AM
    EVENING_PEAK_START = time(17, 30) # 5:30 PM
    EVENING_PEAK_END = time(20, 0)    # 8:00 PM
    
    # Chennai location distances (simplified distance matrix)
    CHENNAI_LOCATIONS = {
        'Maduravoyal': {'lat': 13.0418, 'lng': 80.1435},
        'Sholinganallur': {'lat': 12.9006, 'lng': 80.2279},
        'T. Nagar': {'lat': 13.0418, 'lng': 80.2341},
        'Anna Nagar': {'lat': 13.0850, 'lng': 80.2101},
        'Adyar': {'lat': 13.0067, 'lng': 80.2206},
        'Velachery': {'lat': 12.9750, 'lng': 80.2200},
        'Tambaram': {'lat': 12.9249, 'lng': 80.1000},
        'Porur': {'lat': 13.0382, 'lng': 80.1560},
        'OMR': {'lat': 12.9165, 'lng': 80.2364},
        'ECR': {'lat': 12.8503, 'lng': 80.2925},
        'Guindy': {'lat': 13.0067, 'lng': 80.2070},
        'Chromepet': {'lat': 12.9516, 'lng': 80.1462},
        'Perungalathur': {'lat': 12.9036, 'lng': 80.0890},
        'Pallavaram': {'lat': 12.9675, 'lng': 80.1491},
        'Nanganallur': {'lat': 12.9840, 'lng': 80.1932},
        'Korattur': {'lat': 13.1372, 'lng': 80.1851},
        'Avadi': {'lat': 13.1147, 'lng': 79.9106},
        'Ambattur': {'lat': 13.1143, 'lng': 80.1548},
        'Chennai Central': {'lat': 13.0827, 'lng': 80.2707},
        'Padi': {'lat': 13.1292, 'lng': 80.1622}
    }
    
    @staticmethod
    def calculate_distance(from_location: str, to_location: str) -> float:
        """Calculate distance between two Chennai locations (simplified)"""
        if from_location not in FareService.CHENNAI_LOCATIONS or to_location not in FareService.CHENNAI_LOCATIONS:
            # Default distance for unknown locations
            return 10.0
        
        from_coords = FareService.CHENNAI_LOCATIONS[from_location]
        to_coords = FareService.CHENNAI_LOCATIONS[to_location]
        
        # Simple Euclidean distance calculation (approximation)
        # In real implementation, use Google Maps Distance Matrix API
        lat_diff = abs(from_coords['lat'] - to_coords['lat'])
        lng_diff = abs(from_coords['lng'] - to_coords['lng'])
        
        # Convert coordinate difference to approximate km
        # 1 degree ≈ 111 km (rough approximation)
        distance_km = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111
        
        # Round to 1 decimal place and ensure minimum 2km
        return max(round(distance_km, 1), 2.0)
    
    @staticmethod
    def is_peak_time(departure_time) -> bool:
        """Check if the given time falls in peak hours"""
        if isinstance(departure_time, str):
            try:
                departure_time = datetime.strptime(departure_time, '%H:%M').time()
            except ValueError:
                return False
        
        # Check morning peak
        if FareService.MORNING_PEAK_START <= departure_time <= FareService.MORNING_PEAK_END:
            return True
        
        # Check evening peak
        if FareService.EVENING_PEAK_START <= departure_time <= FareService.EVENING_PEAK_END:
            return True
        
        return False
    
    @staticmethod
    def calculate_fare(from_location: str, to_location: str, departure_time=None, bike_type='bike') -> dict:
        """Calculate fare for a ride"""
        
        # Calculate distance
        distance_km = FareService.calculate_distance(from_location, to_location)
        
        # Base fare calculation
        base_fare = distance_km * FareService.BASE_RATE_PER_KM
        
        # Apply peak time surcharge if applicable
        peak_surcharge = 0
        is_peak = False
        if departure_time:
            is_peak = FareService.is_peak_time(departure_time)
            if is_peak:
                peak_surcharge = base_fare * (FareService.PEAK_TIME_MULTIPLIER - 1)
        
        # Apply long distance discount if applicable
        long_distance_discount = 0
        if distance_km > FareService.LONG_DISTANCE_THRESHOLD:
            discount_amount = base_fare + peak_surcharge
            long_distance_discount = discount_amount * (1 - FareService.LONG_DISTANCE_DISCOUNT)
        
        # Calculate final fare
        final_fare = base_fare + peak_surcharge - long_distance_discount
        
        # Apply minimum fare
        final_fare = max(final_fare, FareService.MIN_FARE)
        
        # Bike type adjustment (optional)
        bike_multiplier = 1.0
        if bike_type.lower() == 'motorcycle':
            bike_multiplier = 1.2  # 20% more for motorcycles
        elif bike_type.lower() == 'scooter':
            bike_multiplier = 0.9   # 10% less for scooters
        
        final_fare *= bike_multiplier
        
        # Round to nearest rupee
        final_fare = round(final_fare, 0)
        
        # Calculate estimated time (assuming 25 km/hr average speed)
        estimated_time_minutes = round((distance_km / 25) * 60, 0)
        
        return {
            'distance_km': distance_km,
            'base_fare': round(base_fare, 2),
            'peak_surcharge': round(peak_surcharge, 2) if peak_surcharge > 0 else 0,
            'long_distance_discount': round(long_distance_discount, 2) if long_distance_discount > 0 else 0,
            'bike_type_multiplier': bike_multiplier,
            'final_fare': int(final_fare),
            'is_peak_time': is_peak,
            'estimated_time_minutes': int(estimated_time_minutes),
            'breakdown': {
                'base_rate_per_km': FareService.BASE_RATE_PER_KM,
                'total_distance': distance_km,
                'peak_time_applied': is_peak,
                'long_distance_discount_applied': distance_km > FareService.LONG_DISTANCE_THRESHOLD,
                'minimum_fare_applied': final_fare == FareService.MIN_FARE
            }
        }
    
    @staticmethod
    def get_fare_estimate(from_location: str, to_location: str, departure_time=None) -> dict:
        """Get a quick fare estimate for route planning"""
        fare_info = FareService.calculate_fare(from_location, to_location, departure_time)
        
        return {
            'from_location': from_location,
            'to_location': to_location,
            'distance_km': fare_info['distance_km'],
            'estimated_fare': fare_info['final_fare'],
            'estimated_time_minutes': fare_info['estimated_time_minutes'],
            'is_peak_time': fare_info['is_peak_time']
        } 