#!/usr/bin/env python3
"""
Route Service for Chennai Bike Ride-Sharing
Integrates OpenStreetMap (OSM), OSRM Road Routing, and Chennai Commuter Geo-Database
with exact door-level addresses, landmarks, metro stations, tech parks, and pincodes.
"""

import math
import requests
import json
import re
from typing import Dict, List, Optional, Tuple, Any

from services.chennai_locations_data import CHENNAI_LOCATIONS_DATABASE

class RouteService:
    """Service for Chennai road geocoding, distance, time, and corridor matching"""
    
    # 150+ Curated Chennai IT Parks, SEZs, Metro Stations, Local Trains, Bus Terminals, Tourist Spots & Hubs
    CHENNAI_HUBS: Dict[str, Dict[str, Any]] = dict(CHENNAI_LOCATIONS_DATABASE)
    
    @classmethod
    def get_coordinates(cls, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Get (lat, lng) for a location name.
        Checks pre-seeded database first, then tries fuzzy match, then Nominatim OSM.
        """
        if not location_name:
            return None
        
        name_clean = location_name.strip()
        name_lower = name_clean.lower()
        
        # 0. Check if raw coordinates passed (e.g. '13.0500,80.2121' or 'Chennai (13.0500, 80.2121)')
        coord_match = re.search(r'([0-9]{1,2}\.[0-9]+)\s*,\s*([0-9]{1,3}\.[0-9]+)', name_clean)
        if coord_match:
            try:
                lat = float(coord_match.group(1))
                lng = float(coord_match.group(2))
                if 12.0 <= lat <= 14.0 and 79.0 <= lng <= 81.0:
                    return (lat, lng)
            except Exception:
                pass
        
        # 1. Exact match in pre-seeded hubs
        for hub_name, data in cls.CHENNAI_HUBS.items():
            if hub_name.lower() == name_lower:
                return (data['lat'], data['lng'])
        
        # 2. Substring match in pre-seeded hubs
        for hub_name, data in cls.CHENNAI_HUBS.items():
            if name_lower in hub_name.lower() or hub_name.lower() in name_lower:
                return (data['lat'], data['lng'])
            if data.get('area', '').lower() in name_lower or name_lower in data.get('area', '').lower():
                return (data['lat'], data['lng'])
            if data.get('address', '').lower() in name_lower or name_lower in data.get('address', '').lower():
                return (data['lat'], data['lng'])
            if data.get('pincode', '') and data.get('pincode', '') in name_clean:
                return (data['lat'], data['lng'])
        
        # 3. Live Nominatim OSM Geocoding (bounded to Chennai)
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{name_clean}, Chennai, Tamil Nadu, India",
                'format': 'json',
                'limit': 1,
                'countrycodes': 'in',
                'viewbox': '79.8,13.4,80.4,12.7'
            }
            headers = {'User-Agent': 'ChennaiSmartRideMatcher/2.0 (contact@smartride.in)'}
            response = requests.get(url, params=params, headers=headers, timeout=4)
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    lat = float(results[0]['lat'])
                    lng = float(results[0]['lon'])
                    # Cache in memory
                    cls.CHENNAI_HUBS[name_clean] = {
                        'lat': lat,
                        'lng': lng,
                        'area': 'Chennai',
                        'pincode': '',
                        'address': results[0].get('display_name', name_clean),
                        'type': 'geocoded'
                    }
                    return (lat, lng)
        except Exception as e:
            print(f"[WARN] Geocoding request failed for {name_clean}: {e}")
        
        # Default fallback to Chennai Central coordinates
        return (13.0827, 80.2707)

    @classmethod
    def reverse_geocode(cls, lat: float, lng: float) -> Dict[str, Any]:
        """
        Reverse geocode GPS coordinates to exact Chennai street address, locality and pincode.
        """
        # 1. First check if within 400m of any pre-seeded Chennai hub
        closest_hub = None
        min_d = 999.0
        for name, data in cls.CHENNAI_HUBS.items():
            d = cls._haversine(lat, lng, data['lat'], data['lng'])
            if d < min_d:
                min_d = d
                closest_hub = (name, data)
                
        if closest_hub and min_d <= 0.4:
            hub_name, hub_data = closest_hub
            return {
                'success': True,
                'name': hub_name,
                'address': hub_data.get('address', f"{hub_name}, Chennai"),
                'pincode': hub_data.get('pincode', ''),
                'lat': lat,
                'lng': lng,
                'area': hub_data.get('area', 'Chennai')
            }
            
        # 2. Query Nominatim reverse API with server-side User-Agent
        try:
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {'User-Agent': 'ChennaiSmartRideMatcher/2.0 (contact@smartride.in)'}
            res = requests.get(url, params=params, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                addr = data.get('address', {})
                display_name = data.get('display_name', '')
                postcode = addr.get('postcode', '')
                
                title = (
                    addr.get('building') or
                    addr.get('amenity') or
                    addr.get('office') or
                    addr.get('road') or
                    addr.get('suburb') or
                    addr.get('neighbourhood') or
                    'Chennai'
                )
                
                # Format clean address
                parts = []
                if addr.get('house_number'):
                    parts.append(f"#{addr['house_number']}")
                if addr.get('road'):
                    parts.append(addr['road'])
                if addr.get('suburb') or addr.get('neighbourhood'):
                    parts.append(addr.get('suburb') or addr.get('neighbourhood'))
                parts.append('Chennai')
                if postcode:
                    parts.append(f"- {postcode}")
                    
                clean_address = ", ".join(parts) if parts else display_name
                
                # Cache in memory
                display_title = f"{title}, {addr.get('suburb', 'Chennai')}" if addr.get('suburb') and title != addr.get('suburb') else title
                cls.CHENNAI_HUBS[display_title] = {
                    'lat': lat,
                    'lng': lng,
                    'area': addr.get('suburb') or 'Chennai',
                    'pincode': postcode,
                    'address': clean_address,
                    'type': 'gps'
                }
                
                return {
                    'success': True,
                    'name': display_title,
                    'address': clean_address,
                    'pincode': postcode,
                    'lat': lat,
                    'lng': lng,
                    'area': addr.get('suburb') or 'Chennai'
                }
        except Exception as e:
            print(f"[WARN] Reverse geocoding failed: {e}")
            
        # Fallback to closest known hub
        if closest_hub:
            hub_name, hub_data = closest_hub
            return {
                'success': True,
                'name': f"Near {hub_name}",
                'address': hub_data.get('address', f"Near {hub_name}, Chennai"),
                'pincode': hub_data.get('pincode', ''),
                'lat': lat,
                'lng': lng,
                'area': hub_data.get('area', 'Chennai')
            }
            
        return {
            'success': True,
            'name': f"Chennai ({lat:.4f}, {lng:.4f})",
            'address': f"Chennai Coordinates ({lat:.4f}, {lng:.4f})",
            'pincode': '600001',
            'lat': lat,
            'lng': lng,
            'area': 'Chennai'
        }

    @classmethod
    def get_locations_list(cls, query: str = '') -> List[Dict[str, Any]]:
        """
        Return list of Chennai locations matching query for autocomplete with exact
        door numbers, roads, tech park buildings, suburbs, and 6-digit pincodes.
        """
        results = []
        q = query.strip().lower()
        
        # 1. Search in curated Chennai Hubs (support multi-token match)
        query_tokens = q.split() if q else []
        
        for name, data in cls.CHENNAI_HUBS.items():
            searchable_text = f"{name} {data.get('area', '')} {data.get('address', '')} {data.get('pincode', '')} {data.get('type', '')}".lower()
            
            match = False
            if not q:
                match = True
            elif all(tok in searchable_text for tok in query_tokens):
                match = True
            elif any(tok in searchable_text for tok in query_tokens) and len(query_tokens) > 1:
                match = True
                
            if match:
                results.append({
                    'name': name,
                    'lat': data['lat'],
                    'lng': data['lng'],
                    'area': data.get('area', 'Chennai'),
                    'pincode': data.get('pincode', ''),
                    'address': data.get('address', f"{name}, Chennai"),
                    'type': data.get('type', 'hub')
                })
        
        # 2. If query is longer and few local matches, perform live OSM Nominatim query
        if len(q) >= 3 and len(results) < 8:
            try:
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': f"{query}, Chennai",
                    'format': 'json',
                    'addressdetails': 1,
                    'limit': 10,
                    'countrycodes': 'in',
                    'viewbox': '79.8,13.4,80.4,12.7'
                }
                headers = {'User-Agent': 'ChennaiSmartRideMatcher/2.0 (contact@smartride.in)'}
                response = requests.get(url, params=params, headers=headers, timeout=3)
                if response.status_code == 200:
                    for item in response.json():
                        addr = item.get('address', {})
                        display_name = item.get('display_name', '')
                        lat = float(item.get('lat', 13.0827))
                        lng = float(item.get('lon', 80.2707))
                        postcode = addr.get('postcode', '')
                        
                        # Extract clean title
                        title = (
                            addr.get('building') or
                            addr.get('amenity') or
                            addr.get('office') or
                            addr.get('road') or
                            addr.get('suburb') or
                            item.get('name') or
                            query.title()
                        )
                        
                        # Avoid duplicates
                        if not any(r['name'].lower() == title.lower() for r in results):
                            results.append({
                                'name': title,
                                'lat': lat,
                                'lng': lng,
                                'area': addr.get('suburb') or addr.get('neighbourhood') or 'Chennai',
                                'pincode': postcode,
                                'address': display_name,
                                'type': 'location'
                            })
            except Exception as e:
                pass

        return results[:40]

    @classmethod
    def calculate_road_route(cls, from_location: str, to_location: str) -> Dict[str, Any]:
        """
        Calculate actual driving road route using OSRM API.
        Returns exact distance (km), duration (mins), and GeoJSON route coordinates polyline.
        """
        from_coords = cls.get_coordinates(from_location)
        to_coords = cls.get_coordinates(to_location)
        
        if not from_coords or not to_coords:
            return cls._generate_fallback_route(from_location, to_location, (13.0418, 80.1435), (13.0135, 80.2030))
        
        from_lat, from_lng = from_coords
        to_lat, to_lng = to_coords
        
        # OSRM Driving API URL
        osrm_url = f"https://router.project-osrm.org/route/v1/driving/{from_lng},{from_lat};{to_lng},{to_lat}?overview=full&geometries=geojson"
        
        try:
            response = requests.get(osrm_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 'Ok' and len(data.get('routes', [])) > 0:
                    route = data['routes'][0]
                    distance_km = round(route['distance'] / 1000, 1)
                    duration_mins = max(1, round(route['duration'] / 60))
                    
                    # Convert [lng, lat] to [lat, lng] for Leaflet
                    raw_coords = route['geometry']['coordinates']
                    leaflet_coords = [[coord[1], coord[0]] for coord in raw_coords]
                    
                    return {
                        'success': True,
                        'distance_km': distance_km,
                        'duration_mins': duration_mins,
                        'coordinates': leaflet_coords,
                        'from_coords': {'lat': from_lat, 'lng': from_lng},
                        'to_coords': {'lat': to_lat, 'lng': to_lng},
                        'source': 'osrm'
                    }
        except Exception as e:
            print(f"[WARN] OSRM routing failed ({from_location} -> {to_location}): {e}")
        
        # Mathematical fallback
        return cls._generate_fallback_route(from_location, to_location, from_coords, to_coords)

    @classmethod
    def _generate_fallback_route(cls, from_name: str, to_name: str, from_c: Tuple[float, float], to_c: Tuple[float, float]) -> Dict[str, Any]:
        """Generate smooth geometric road approximation when OSRM is offline"""
        lat1, lng1 = from_c
        lat2, lng2 = to_c
        
        # Haversine straight-line distance * 1.35 road factor
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        straight_km = 6371 * c
        road_km = round(straight_km * 1.35, 1)
        duration_mins = max(1, round(road_km * 2.2)) # ~25-30 km/h Chennai traffic
        
        # Generate 20 intermediate curved polyline points
        steps = 20
        coords = []
        for i in range(steps + 1):
            t = i / steps
            inter_lat = lat1 + (lat2 - lat1) * t
            inter_lng = lng1 + (lng2 - lng1) * t
            # Subtle curvature
            curve = math.sin(t * math.pi) * 0.006
            coords.append([inter_lat + curve, inter_lng + curve])
            
        return {
            'success': True,
            'distance_km': max(road_km, 1.0),
            'duration_mins': max(duration_mins, 3),
            'coordinates': coords,
            'from_coords': {'lat': lat1, 'lng': lng1},
            'to_coords': {'lat': lat2, 'lng': lng2},
            'source': 'geometric_fallback'
        }

    @classmethod
    def calculate_corridor_overlap(cls, rider_route_coords: List[List[float]], passenger_pickup: Tuple[float, float], passenger_drop: Tuple[float, float]) -> Dict[str, Any]:
        """
        Check if passenger's pickup and drop-off points fall along the rider's travel corridor.
        """
        if not rider_route_coords or len(rider_route_coords) == 0:
            return {'on_route': False, 'min_pickup_dist_km': 99.0, 'detour_mins': 99}
        
        p_lat, p_lng = passenger_pickup
        d_lat, d_lng = passenger_drop
        
        min_p_dist = min([cls._haversine(p_lat, p_lng, c[0], c[1]) for c in rider_route_coords])
        min_d_dist = min([cls._haversine(d_lat, d_lng, c[0], c[1]) for c in rider_route_coords])
        
        on_route = (min_p_dist <= 2.2) and (min_d_dist <= 2.5)
        detour_mins = max(0, round((min_p_dist + min_d_dist) * 2.0))
        
        return {
            'on_route': on_route,
            'min_pickup_dist_km': round(min_p_dist, 2),
            'min_drop_dist_km': round(min_d_dist, 2),
            'detour_mins': detour_mins
        }

    @classmethod
    def calculate_corridor_match(cls, rider_from: str, rider_to: str, pax_from: str, pax_to: str) -> Dict[str, Any]:
        """
        Calculate corridor match score (0-100%), detour time, pickup suggestion, and compatibility
        between a rider's route and a passenger's requested route.
        """
        r_from_clean = rider_from.strip().lower()
        r_to_clean = rider_to.strip().lower()
        p_from_clean = pax_from.strip().lower()
        p_to_clean = pax_to.strip().lower()

        # 1. Direct or substring match
        if (r_from_clean == p_from_clean or p_from_clean in r_from_clean or r_from_clean in p_from_clean) and \
           (r_to_clean == p_to_clean or p_to_clean in r_to_clean or r_to_clean in p_to_clean):
            return {
                'match_score': 98,
                'match_type': 'exact_corridor',
                'reasoning': f"Perfect match! Rider travels directly from {rider_from} to {rider_to}.",
                'pickup_suggestion': f"Board directly at {pax_from}",
                'detour_time': 0,
                'compatibility': 'Perfect'
            }

        # 2. Get road coordinates for rider's route
        rider_road = cls.calculate_road_route(rider_from, rider_to)
        pax_pickup_coords = cls.get_coordinates(pax_from)
        pax_drop_coords = cls.get_coordinates(pax_to)

        if not pax_pickup_coords or not pax_drop_coords:
            is_sub = (p_from_clean in r_from_clean or r_from_clean in p_from_clean)
            return {
                'match_score': 85 if is_sub else 60,
                'match_type': 'corridor_overlap' if is_sub else 'approximate_corridor',
                'reasoning': f"Commuter route along {rider_from} ➔ {rider_to} corridor.",
                'pickup_suggestion': f"Meet at {pax_from} junction",
                'detour_time': 2 if is_sub else 5,
                'compatibility': 'High' if is_sub else 'Moderate'
            }

        coords = rider_road.get('coordinates', [])
        overlap = cls.calculate_corridor_overlap(coords, pax_pickup_coords, pax_drop_coords)

        pickup_dist = overlap['min_pickup_dist_km']
        drop_dist = overlap['min_drop_dist_km']
        detour = overlap['detour_mins']

        if pickup_dist <= 1.2 and drop_dist <= 1.2:
            score = 96 - int(detour * 1.5)
            match_type = 'direct_corridor'
            reasoning = f"Direct overlap! Rider passes right through {pax_from} on the way to {rider_to} ({detour} min detour)."
        elif pickup_dist <= 2.5 and drop_dist <= 2.5:
            score = 88 - int(detour * 2)
            match_type = 'corridor_overlap'
            reasoning = f"Corridor match! {pax_from} is along the {rider_from} ➔ {rider_to} route ({detour} min detour)."
        elif pickup_dist <= 4.0 and drop_dist <= 4.0:
            score = 72 - int(detour * 2)
            match_type = 'nearby_corridor'
            reasoning = f"Nearby corridor ({detour} min detour). Suggested pickup near {pax_from}."
        else:
            score = max(35, 60 - int((pickup_dist + drop_dist) * 3))
            match_type = 'partial_corridor'
            reasoning = f"Connecting commute route between {rider_from} and {rider_to}."

        return {
            'match_score': max(30, min(99, score)),
            'match_type': match_type,
            'reasoning': reasoning,
            'pickup_suggestion': f"Board near {pax_from} main road junction",
            'detour_time': detour,
            'compatibility': 'High' if score >= 80 else 'Moderate' if score >= 60 else 'Fair'
        }

    @staticmethod
    def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate straight line distance in km between two coordinates"""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
