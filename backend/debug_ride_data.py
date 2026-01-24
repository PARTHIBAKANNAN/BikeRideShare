#!/usr/bin/env python3
"""
Debug ride data and Azure OpenAI client
"""

from models.models import db, Ride
from app import create_app
import openai
from config.settings import Config

def debug_ride_data():
    app = create_app('development')
    with app.app_context():
        print("=== DEBUGGING RIDE DATA ===")
        ride = Ride.query.first()
        if ride:
            print('Raw ride data:')
            print(f'  from_location: {ride.from_location}')
            print(f'  to_location: {ride.to_location}')
            print(f'  departure_date: {ride.departure_date}')
            
            print('\nRide to_dict():')
            ride_dict = ride.to_dict()
            print(f'  Keys: {list(ride_dict.keys())}')
            print(f'  from_location: {ride_dict.get("from_location")}')
            print(f'  to_location: {ride_dict.get("to_location")}')
            print(f'  route: {ride_dict.get("route")}')
        else:
            print('No rides found')

def test_azure_openai():
    print("\n=== TESTING AZURE OPENAI ===")
    print(f'API Key present: {bool(Config.AZURE_OPENAI_API_KEY)}')
    print(f'Endpoint: {Config.AZURE_OPENAI_ENDPOINT}')
    print(f'Deployment: {Config.AZURE_OPENAI_DEPLOYMENT_NAME}')
    print(f'API Version: {Config.AZURE_OPENAI_API_VERSION}')
    
    try:
        # Try different client initialization
        client = openai.AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        print("✅ Azure OpenAI client created successfully")
        
        # Test a simple completion
        response = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'AI connection successful!'"}
            ],
            max_tokens=10
        )
        
        print(f"✅ AI Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI failed: {e}")
        return False

if __name__ == "__main__":
    debug_ride_data()
    test_azure_openai() 