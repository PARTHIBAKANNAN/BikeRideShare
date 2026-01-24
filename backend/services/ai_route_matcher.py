#!/usr/bin/env python3
"""
AI-Powered Route Matching Service using Azure OpenAI GPT-4
Intelligently matches rides based on route analysis, proximity, and via points
"""

import openai
import json
import os
from typing import List, Dict, Any
from config.settings import Config

class AIRouteMatcher:
    """AI-powered intelligent route matching using GPT-4"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.client = None
        self.is_configured = False
        
        if Config.is_azure_configured():
            try:
                # Updated initialization to avoid proxies argument issue
                import openai
                
                # Set the global configuration
                openai.api_type = "azure"
                openai.api_key = Config.AZURE_OPENAI_API_KEY
                openai.api_base = Config.AZURE_OPENAI_ENDPOINT
                openai.api_version = Config.AZURE_OPENAI_API_VERSION
                
                # Create client with minimal arguments
                self.client = openai.AzureOpenAI(
                    api_key=Config.AZURE_OPENAI_API_KEY,
                    api_version=Config.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
                )
                self.deployment_name = Config.AZURE_OPENAI_DEPLOYMENT_NAME
                self.is_configured = True
                print("✅ Azure OpenAI configured successfully")
            except Exception as e:
                print(f"⚠️ Azure OpenAI configuration failed: {e}")
                # Fallback to basic matching
                self.is_configured = False
    
    def find_intelligent_matches(self, search_request: Dict, available_rides: List[Dict]) -> List[Dict]:
        """
        Use AI to find intelligent ride matches based on route analysis
        
        Args:
            search_request: User's search criteria (from, to, date, etc.)
            available_rides: List of available rides to analyze
            
        Returns:
            List of rides with AI-calculated match scores and reasons
        """
        if not self.is_configured:
            # Fallback to basic matching if AI not configured
            return self._basic_route_matching(search_request, available_rides)
        
        try:
            # Prepare context for GPT
            context = self._prepare_context(search_request, available_rides)
            
            # Get AI analysis
            ai_response = self._call_gpt_route_analysis(context)
            
            # Parse and rank results
            matched_rides = self._parse_ai_response(ai_response, available_rides)
            
            return matched_rides
            
        except Exception as e:
            print(f"❌ AI route matching failed: {e}")
            # Fallback to basic matching
            return self._basic_route_matching(search_request, available_rides)
    
    def _prepare_context(self, search_request: Dict, available_rides: List[Dict]) -> str:
        """Prepare context for GPT analysis"""
        
        user_route = f"{search_request.get('from_location')} to {search_request.get('to_location')}"
        
        # Chennai location context and major routes
        chennai_context = """
        Chennai Major Areas and Routes:
        
        NORTH: Anna Nagar, Avadi, Ambattur, Korattur, Padi
        CENTRAL: T. Nagar, Egmore, Chennai Central, Nungambakkam, Kodambakkam
        SOUTH: Adyar, Thiruvanmiyur, Sholinganallur, Velachery, Tambaram
        WEST: Porur, Maduravoyal, Pallavaram, Chromepet
        EAST: ECR, OMR, Thoraipakkam, Besant Nagar
        
        Major Routes:
        - OMR (Old Mahabalipuram Road): Sholinganallur ↔ Chennai Central via Thoraipakkam, Velachery
        - GST Road: Tambaram ↔ Chennai Central via Pallavaram, Guindy  
        - Anna Salai: T. Nagar ↔ Chennai Central via Nungambakkam
        - Mount Road: Guindy ↔ Chennai Central via Nandanam, Teynampet
        - Poonamallee High Road: Porur ↔ Chennai Central via Maduravoyal, Koyambedu
        
        Traffic & Distance Considerations:
        - Peak hours: 8-10 AM, 6-8 PM (heavy traffic)
        - OMR to City Center: 45-60 min normal, 90+ min peak
        - Cross-city routes often have good ride-sharing potential
        """
        
        rides_info = []
        for i, ride in enumerate(available_rides):
            # Access ride data from correct nested structure
            route = ride.get('route', {})
            timing = ride.get('timing', {})
            booking = ride.get('booking', {})
            
            ride_route = f"{route.get('from_location', 'Unknown')} to {route.get('to_location', 'Unknown')}"
            timing_info = f"{timing.get('departure_date', 'TBD')} at {timing.get('departure_time', 'TBD')}"
            seats = booking.get('available_seats', 0)
            fare = booking.get('cost_per_person', 0)
            
            rides_info.append(f"Ride {i+1}: {ride_route} | {timing_info} | {seats} seats | ₹{fare}")
        
        context = f"""
        {chennai_context}
        
        USER SEARCH REQUEST:
        Route: {user_route}
        Date: {search_request.get('departure_date', 'Any')}
        Seats needed: {search_request.get('seats_needed', 1)}
        
        AVAILABLE RIDES:
        {chr(10).join(rides_info)}
        
        TASK: Analyze each ride and provide intelligent matching based on:
        1. Direct route overlap (same source/destination)
        2. Via route potential (ride passes through or near user's route)
        3. Reverse route sharing (return journey potential)
        4. Geographical proximity and traffic patterns
        5. Time compatibility and convenience
        
        For each ride, provide a match score (0-100) and detailed reasoning.
        """
        
        return context
    
    def _call_gpt_route_analysis(self, context: str) -> str:
        """Call GPT for route analysis"""
        
        system_prompt = """
        You are an expert Chennai route analyst for a ride-sharing app. 
        Analyze rides intelligently considering:
        - Route overlaps and via points
        - Chennai geography and traffic patterns  
        - Practical ride-sharing scenarios
        - Time and convenience factors
        
        Respond with JSON format:
        {
          "matches": [
            {
              "ride_index": 0,
              "match_score": 85,
              "match_type": "via_route",
              "reasoning": "This ride goes from Porur to Sholinganallur via OMR, perfect pickup at Maduravoyal",
              "pickup_suggestion": "Maduravoyal Junction",
              "detour_time": "5 minutes",
              "compatibility": "high"
            }
          ]
        }
        
        Match types: exact_match, via_route, nearby_route, reverse_route, cross_city
        Match scores: 90-100 (excellent), 70-89 (good), 50-69 (fair), 30-49 (poor), 0-29 (not suitable)
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"GPT API call failed: {e}")
    
    def _parse_ai_response(self, ai_response: str, available_rides: List[Dict]) -> List[Dict]:
        """Parse GPT response and enhance ride data"""
        
        # Debug: Print the raw AI response
        print(f"\n🤖 DEBUG: Raw AI Response:")
        print("-" * 50)
        print(ai_response[:500] + "..." if len(ai_response) > 500 else ai_response)
        print("-" * 50)
        
        try:
            # Clean the response - remove markdown code blocks if present
            clean_response = ai_response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]  # Remove ```json
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]  # Remove ```
            clean_response = clean_response.strip()
            
            print(f"🧹 DEBUG: Cleaned response length: {len(clean_response)}")
            
            # Extract JSON from response
            response_data = json.loads(clean_response)
            matches = response_data.get('matches', [])
            
            enhanced_rides = []
            
            print(f"🔍 DEBUG: Found {len(matches)} matches in AI response")
            
            for match in matches:
                ride_index = match.get('ride_index', 0)
                
                print(f"   Processing match: ride_index={ride_index}, available_rides={len(available_rides)}")
                
                if 0 <= ride_index < len(available_rides):
                    ride = available_rides[ride_index].copy()
                    
                    # Add AI analysis
                    ride['ai_match_score'] = match.get('match_score', 0)
                    ride['ai_match_type'] = match.get('match_type', 'unknown')
                    ride['ai_reasoning'] = match.get('reasoning', '')
                    ride['ai_pickup_suggestion'] = match.get('pickup_suggestion', '')
                    ride['ai_detour_time'] = match.get('detour_time', '')
                    ride['ai_compatibility'] = match.get('compatibility', 'unknown')
                    
                    print(f"   ✅ Added ride with score: {ride['ai_match_score']}%")
                    
                    # Include ALL rides with any score (was >= 30, now >= 0)
                    if ride['ai_match_score'] >= 0:
                        enhanced_rides.append(ride)
                else:
                    print(f"   ❌ Invalid ride_index: {ride_index}")
            
            print(f"🎯 DEBUG: Returning {len(enhanced_rides)} enhanced rides")
            
            # Sort by AI match score (highest first)
            enhanced_rides.sort(key=lambda x: x.get('ai_match_score', 0), reverse=True)
            
            return enhanced_rides
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"   Response snippet: {ai_response[:200]}...")
            # If JSON parsing fails, try to extract match info manually
            return self._manual_parse_fallback(ai_response, available_rides)
        except Exception as e:
            print(f"❌ AI response parsing failed: {e}")
            return available_rides[:10]  # Return top 10 as fallback
    
    def _manual_parse_fallback(self, ai_response: str, available_rides: List[Dict]) -> List[Dict]:
        """Fallback manual parsing if JSON parsing fails"""
        
        enhanced_rides = []
        
        # Simple scoring based on keywords in AI response
        for i, ride in enumerate(available_rides):
            ride_copy = ride.copy()
            
            # Basic keyword-based scoring
            score = 50  # Base score
            
            route_mentions = ai_response.lower().count(ride.get('from_location', '').lower())
            route_mentions += ai_response.lower().count(ride.get('to_location', '').lower())
            
            if 'excellent' in ai_response.lower() and route_mentions > 0:
                score = 90
            elif 'good' in ai_response.lower() and route_mentions > 0:
                score = 75
            elif 'via' in ai_response.lower() and route_mentions > 0:
                score = 80
            elif route_mentions > 0:
                score = 60
            
            ride_copy['ai_match_score'] = score
            ride_copy['ai_match_type'] = 'analyzed'
            ride_copy['ai_reasoning'] = f"Route analysis completed (score: {score})"
            
            enhanced_rides.append(ride_copy)
        
        # Sort by score
        enhanced_rides.sort(key=lambda x: x.get('ai_match_score', 0), reverse=True)
        
        return enhanced_rides[:10]
    
    def _basic_route_matching(self, search_request: Dict, available_rides: List[Dict]) -> List[Dict]:
        """Fallback basic matching when AI is not available"""
        
        user_from = search_request.get('from_location', '').lower()
        user_to = search_request.get('to_location', '').lower()
        
        scored_rides = []
        
        for ride in available_rides:
            ride_copy = ride.copy()
            score = 0
            
            # Access nested route data
            route = ride.get('route', {})
            ride_from = route.get('from_location', '').lower()
            ride_to = route.get('to_location', '').lower()
            
            # Exact match
            if user_from == ride_from and user_to == ride_to:
                score = 100
            # Source match
            elif user_from == ride_from:
                score = 70
            # Destination match  
            elif user_to == ride_to:
                score = 70
            # Partial match
            elif user_from in ride_from or ride_from in user_from:
                score = 50
            elif user_to in ride_to or ride_to in user_to:
                score = 50
            else:
                score = 20
            
            ride_copy['ai_match_score'] = score
            ride_copy['ai_match_type'] = 'basic'
            ride_copy['ai_reasoning'] = 'Basic route matching (AI not configured)'
            
            scored_rides.append(ride_copy)
        
        # Sort by score
        scored_rides.sort(key=lambda x: x.get('ai_match_score', 0), reverse=True)
        
        return scored_rides[:10]

# Global instance
ai_route_matcher = AIRouteMatcher() 