# nest_client.py
import os
import pickle
import requests
import logging
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import (
    NEST_PROJECT_ID,
    NEST_CLIENT_ID,
    NEST_CLIENT_SECRET,
    REDIRECT_URI,
    SCOPES,
    AUTH_URL,
    TOKEN_URL
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NestClient:
    def __init__(self):
        self.credentials = None
        self.device_id = None
        self.token_file = 'nest_token.pickle'
        self.project_id = NEST_PROJECT_ID
        self._load_or_refresh_credentials()
        if self.credentials:
            self._discover_project_id()
            self._initialize_device()

    def _discover_project_id(self):
        """Discover the correct project ID for the SDM API."""
        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # List all available enterprises
            url = 'https://smartdevicemanagement.googleapis.com/v1/enterprises'
            logger.info(f"Discovering available enterprises from {url}...")
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            enterprises = response.json().get('enterprises', [])
            if enterprises:
                self.project_id = enterprises[0]['name'].split('/')[-1]
                logger.info(f"Found enterprise ID: {self.project_id}")
            else:
                logger.warning("No enterprises found. Using project ID from config.")
                
        except Exception as e:
            logger.error(f"Error discovering project ID: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.content}")
            # Fall back to project ID from config
            logger.info(f"Falling back to configured project ID: {self.project_id}")

    def _load_or_refresh_credentials(self):
        """Load existing credentials or initialize new ones."""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                try:
                    self.credentials = pickle.load(token)
                    logger.info("Loaded existing credentials from token file.")
                except Exception as e:
                    logger.error(f"Error loading token file: {e}")
                    self.credentials = None

        # If there are no (valid) credentials available, let's create new ones
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.credentials, token)
                        logger.info("Credentials refreshed successfully.")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    self.credentials = None

            if not self.credentials:
                logger.info("No valid credentials available. Initiating OAuth flow.")
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": NEST_CLIENT_ID,
                            "project_id": NEST_PROJECT_ID,
                            "client_secret": NEST_CLIENT_SECRET,
                            "redirect_uris": [REDIRECT_URI],
                            "auth_uri": AUTH_URL,
                            "token_uri": TOKEN_URL,
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                        }
                    },
                    SCOPES
                )
                
                try:
                    self.credentials = flow.run_local_server(
                        host='localhost',
                        port=8080,  # Must match the port in REDIRECT_URI
                        authorization_prompt_message="Please visit the following URL to authorize the application:",
                        success_message="Authorization successful! You may close this window.",
                        open_browser=True
                    )
                    
                    # Save the credentials for the next run
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.credentials, token)
                        logger.info("Credentials saved successfully.")
                        
                except Exception as e:
                    logger.error(f"Error during authorization: {e}")
                    raise

    def _initialize_device(self):
        """Initialize the first available Nest thermostat device."""
        if not self.credentials:
            logger.error("No valid credentials available.")
            return

        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }

        try:
            url = f'https://smartdevicemanagement.googleapis.com/v1/enterprises/{self.project_id}/devices'
            logger.info(f"Fetching devices from: {url}")
            
            response = requests.get(url, headers=headers)
            if response.status_code == 401:
                logger.error("Unauthorized access. Check your access token.")
                response.raise_for_status()
            
            response.raise_for_status()
            
            devices = response.json().get('devices', [])
            logger.info(f"Found {len(devices)} devices.")
            
            for device in devices:
                device_type = device.get('type', '')
                logger.info(f"Found device type: {device_type}")
                if 'sdm.devices.types.THERMOSTAT' in device_type:
                    self.device_id = device['name']
                    logger.info(f"Found thermostat device: {self.device_id}")
                    return

            if not self.device_id:
                logger.error("No thermostat devices found.")
                
        except Exception as e:
            logger.error(f"Error initializing Nest device: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.content}")
            raise

    def get_current_temperature(self):
        """Get the current temperature from the thermostat."""
        if not self.device_id or not self.credentials:
            logger.error("Device not initialized or no valid credentials.")
            return None

        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }

        try:
            url = f'https://smartdevicemanagement.googleapis.com/v1/{self.device_id}'
            logger.info(f"Fetching current temperature from: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            traits = response.json().get('traits', {})
            temp = traits.get('sdm.devices.traits.Temperature', {}).get('ambientTemperatureCelsius')
            
            if temp is not None:
                logger.info(f"Current temperature: {temp}°C")
            else:
                logger.warning("Temperature reading is None.")
                
            return temp

        except Exception as e:
            logger.error(f"Error getting temperature: {e}")
            return None

    def set_temperature(self, target_temp):
        """Set the target temperature on the thermostat."""
        if not self.device_id or not self.credentials:
            logger.error("Device not initialized or no valid credentials.")
            return False

        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }

        data = {
            'command': 'sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat',
            'params': {
                'heatCelsius': float(target_temp)
            }
        }

        try:
            url = f'https://smartdevicemanagement.googleapis.com/v1/{self.device_id}:executeCommand'
            logger.info(f"Setting temperature to {target_temp}°C via: {url}")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            logger.info(f"Successfully set temperature to {target_temp}°C.")
            return True

        except Exception as e:
            logger.error(f"Error setting temperature: {e}")
            return False

    def set_hot_water_state(self, is_on):
        """Set the hot water state."""
        if not self.device_id or not self.credentials:
            logger.error("Device not initialized or no valid credentials.")
            return False

        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }

        data = {
            'command': 'sdm.devices.commands.HotWater.SetMode',
            'params': {
                'mode': 'HEAT' if is_on else 'OFF'
            }
        }

        try:
            url = f'https://smartdevicemanagement.googleapis.com/v1/{self.device_id}:executeCommand'
            state_str = 'ON' if is_on else 'OFF'
            logger.info(f"Setting hot water to {state_str} via: {url}")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            logger.info(f"Successfully set hot water to: {state_str}.")
            return True

        except Exception as e:
            logger.error(f"Error setting hot water state: {e}")
            return False

    def refresh_token_if_needed(self):
        """Refresh the access token if it's expired."""
        if not self.credentials:
            logger.error("No credentials available to refresh.")
            return False

        if not self.credentials.valid:
            if self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(self.credentials, token)
                    logger.info("Token refreshed successfully.")
                    return True
                except Exception as e:
                    logger.error(f"Error refreshing token: {e}")
                    return False
        return True