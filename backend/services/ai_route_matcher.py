#!/usr/bin/env python3
"""
AI & Algorithmic Route Matcher for Chennai Bike Ride Sharing
Combines Geometric Corridor Analysis (OSRM) with Google Gemini AI for smart matching
"""

import json
import re
from typing import List, Dict, Any, Optional
from config.settings import Config
from services.route_service import RouteService


class AIRouteMatcher:
    """Intelligent Route Matching Engine using OSRM Road Geometry and Google Gemini AI"""
    
    def __init__(self):
        self.is_configured = False
        self.gemini_key = Config.GEMINI_API_KEY
        self.gemini_model = Config.GEMINI_MODEL or 'gemini-1.5-flash'
        
        if Config.is_gemini_configured():
            self.is_configured = True
            print("[OK] Google Gemini AI Route Matcher initialized")
        else:
            print("[INFO] Gemini API key not provided - running in High-Precision Algorithmic Mode")
            
    def find_intelligent_matches(self, search_request: Dict[str, Any], available_rides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Match available rides against search criteria using road corridor geometry + optional Gemini AI
        """
        if not available_rides:
            return []
            
        pax_from = search_request.get('from_location', '').strip()
        pax_to = search_request.get('to_location', '').strip()
        
        # Step 1: Compute high-precision geometric corridor matching for all candidate rides
        geo_matched_rides = []
        for ride in available_rides:
            ride_copy = dict(ride)
            route = ride.get('route', {})
            rider_from = route.get('from_location', ride.get('from_location', ''))
            rider_to = route.get('to_location', ride.get('to_location', ''))
            
            # Geometric corridor overlap analysis
            geo_match = RouteService.calculate_corridor_match(rider_from, rider_to, pax_from, pax_to)
            
            ride_copy['ai_match_score'] = geo_match['match_score']
            ride_copy['ai_match_type'] = geo_match['match_type']
            ride_copy['ai_reasoning'] = geo_match['reasoning']
            ride_copy['ai_pickup_suggestion'] = geo_match['pickup_suggestion']
            ride_copy['ai_detour_time'] = geo_match['detour_time']
            ride_copy['ai_compatibility'] = geo_match['compatibility']
            
            # Also attach road coordinates if not already present
            if 'route_geometry' not in ride_copy:
                try:
                    road_info = RouteService.calculate_road_route(rider_from, rider_to)
                    ride_copy['route_coordinates'] = road_info.get('coordinates', [])
                    ride_copy['distance_km'] = road_info.get('distance_km', 10.0)
                    ride_copy['duration_minutes'] = road_info.get('duration_minutes', 25)
                except Exception:
                    pass
                    
            geo_matched_rides.append(ride_copy)
            
        # Sort by match score descending
        geo_matched_rides.sort(key=lambda x: x.get('ai_match_score', 0), reverse=True)
        
        # Step 2: If Gemini AI is configured, enhance top candidates with AI commute analysis
        if self.is_configured and len(geo_matched_rides) > 0:
            try:
                enhanced_rides = self._enhance_with_gemini(search_request, geo_matched_rides[:5])
                # Merge back top enhanced rides with the rest
                merged_rides = enhanced_rides + geo_matched_rides[len(enhanced_rides):]
                merged_rides.sort(key=lambda x: x.get('ai_match_score', 0), reverse=True)
                return merged_rides
            except Exception as e:
                print(f"⚠️ Gemini enhancement failed, returning geometric matches: {e}")
                
        return geo_matched_rides

    def _enhance_with_gemini(self, search_request: Dict[str, Any], top_rides: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Call Google Gemini API for Chennai-specific commute tips and natural language advice"""
        import requests
        
        pax_from = search_request.get('from_location')
        pax_to = search_request.get('to_location')
        departure_date = search_request.get('departure_date', 'Today')
        
        rides_summary = []
        for i, ride in enumerate(top_rides):
            route = ride.get('route', {})
            r_from = route.get('from_location', ride.get('from_location'))
            r_to = route.get('to_location', ride.get('to_location'))
            timing = ride.get('timing', {})
            time_str = timing.get('departure_time', 'Morning')
            score = ride.get('ai_match_score', 80)
            rides_summary.append(f"Ride {i+1}: From {r_from} to {r_to} at {time_str} (Algorithmic Score: {score}%)")
            
        prompt = f"""
You are an expert Chennai commute assistant for a bike ride-sharing app.
Passenger is traveling from: "{pax_from}" to "{pax_to}" on {departure_date}.

Candidate Rides:
{chr(10).join(rides_summary)}

For each ride, provide a refined match score (0-100), concise reasoning tailored to Chennai traffic/landmarks (e.g. OMR, GST Road, 100ft Road, Metro hubs), suggested boarding junction, and detour time.

Respond strictly in valid JSON format:
{{
  "matches": [
    {{
      "ride_index": 0,
      "refined_score": 95,
      "reasoning": "Direct route along main corridor with easy pickup.",
      "pickup_suggestion": "Near main bus stop / metro station",
      "detour_time": "0-3 minutes",
      "compatibility": "high"
    }}
  ]
}}
"""
        
        # Call Gemini REST endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1000
            }
        }
        
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=4)
        if response.status_code == 200:
            res_data = response.json()
            candidates = res_data.get('candidates', [])
            if candidates:
                text_content = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                # Clean Markdown code fences
                json_str = re.sub(r'```json\s*|\s*```', '', text_content).strip()
                parsed = json.loads(json_str)
                matches = parsed.get('matches', [])
                
                for item in matches:
                    idx = item.get('ride_index', 0)
                    if 0 <= idx < len(top_rides):
                        top_rides[idx]['ai_match_score'] = item.get('refined_score', top_rides[idx]['ai_match_score'])
                        top_rides[idx]['ai_reasoning'] = item.get('reasoning', top_rides[idx]['ai_reasoning'])
                        top_rides[idx]['ai_pickup_suggestion'] = item.get('pickup_suggestion', top_rides[idx]['ai_pickup_suggestion'])
                        top_rides[idx]['ai_detour_time'] = item.get('detour_time', top_rides[idx]['ai_detour_time'])
                        top_rides[idx]['ai_compatibility'] = item.get('compatibility', top_rides[idx]['ai_compatibility'])
                        
        return top_rides


# Global singleton instance
ai_route_matcher = AIRouteMatcher()