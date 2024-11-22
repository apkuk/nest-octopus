# api_integrations.py
import requests
from datetime import datetime, timezone, timedelta
import logging
from config import (
    OCTOPUS_API_KEY, 
    NEST_CLIENT_ID,
    NEST_CLIENT_SECRET,
    AGILE_PRODUCT_CODE
)

class OctopusClient:
    def __init__(self):
        self.api_key = OCTOPUS_API_KEY
        self.base_url = "https://api.octopus.energy/v1"
        
    def get_rates(self, hours_ahead=4):
        now = datetime.now(timezone.utc)
        params = {
            'period_from': now.strftime("%Y-%m-%dT%H:%M:00Z"),
            'period_to': (now + timedelta(hours=hours_ahead)).strftime("%Y-%m-%dT%H:%M:00Z")
        }
        
        url = f"{self.base_url}/products/{AGILE_PRODUCT_CODE}/electricity-tariffs/E-1R-{AGILE_PRODUCT_CODE}-C/standard-unit-rates/"
        response = requests.get(url, auth=(self.api_key, ''), params=params)
        response.raise_for_status()
        return response.json()['results']

class NestClient:
    def __init__(self):
        self.client_id = NEST_CLIENT_ID
        self.client_secret = NEST_CLIENT_SECRET
        self.base_url = "https://smartdevicemanagement.googleapis.com/v1"
        self.token = None
        
    def refresh_token(self):
        auth_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self._get_refresh_token()
        }
        response = requests.post(auth_url, data=data)
        response.raise_for_status()
        self.token = response.json()['access_token']
        
    def get_device_data(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f"{self.base_url}/enterprises/{self.project_id}/devices", headers=headers)
        response.raise_for_status()
        return response.json()

class WeatherClient:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        
    def get_forecast(self, latitude, longitude, hours=24):
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'hourly': 'temperature_2m,precipitation_probability',
            'forecast_hours': hours
        }
        response = requests.get(f"{self.base_url}/forecast", params=params)
        response.raise_for_status()
        return response.json()