# octopus_client.py
import os
import requests
import logging
from datetime import datetime, timezone
from config import OCTOPUS_API_KEY

logger = logging.getLogger(__name__)

class OctopusClient:
    def __init__(self):
        self.api_key = OCTOPUS_API_KEY
        self.base_url = "https://api.octopus.energy/v1/"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }

    def get_current_rate(self):
        """
        Fetch the current electricity rate.
        
        Returns:
            float: The current electricity rate in pence per kWh.
            None: If there was an error fetching the rate.
        """
        try:
            # Define the product and tariff codes
            # These should ideally come from configuration or environment variables
            product_code = "AGILE-FLEX-22-11-25"
            tariff_code = "E-1R-AGILE-FLEX-22-11-25-B"
            
            # Construct the URL for the current rate
            url = f"{self.base_url}products/{product_code}/electricity-tariffs/{tariff_code}/rates/"
            
            # Make the API request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
            
            data = response.json()
            
            # Validate the response structure
            if 'results' not in data or not data['results']:
                logger.error("No rate results found in the response.")
                return None
            
            # Get the current UTC time to find the matching rate
            now_utc = datetime.now(timezone.utc)
            current_hour = now_utc.hour
            current_minute = now_utc.minute
            logger.debug(f"Current UTC time: {now_utc.isoformat()}")

            # Iterate through the rates to find the one that matches the current time
            for rate in data['results']:
                valid_from = rate.get('valid_from')
                valid_to = rate.get('valid_to')
                
                if not valid_from or not valid_to:
                    continue  # Skip if time information is incomplete
                
                # Parse the valid_from and valid_to times
                valid_from_dt = datetime.fromisoformat(valid_from.rstrip('Z')).replace(tzinfo=timezone.utc)
                valid_to_dt = datetime.fromisoformat(valid_to.rstrip('Z')).replace(tzinfo=timezone.utc)
                
                if valid_from_dt <= now_utc < valid_to_dt:
                    current_rate = rate.get('value_inc_vat')
                    logger.info(f"Current electricity rate: {current_rate}p/kWh (Valid from {valid_from} to {valid_to})")
                    return current_rate
            
            # If no matching rate is found, log an error
            logger.error("No matching rate found for the current time.")
            return None

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching current rate: {http_err} - Response: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error occurred while fetching current rate: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout error occurred while fetching current rate: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request exception occurred while fetching current rate: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON decoding failed: {json_err} - Response Content: {response.content}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching current rate: {e}")
        
        return None

    def get_current_gas_rate(self):
        """
        Fetch the current gas rate.
        
        Returns:
            float: The current gas rate in pence per kWh.
            None: If there was an error fetching the rate.
        """
        try:
            # Define the product and tariff codes
            # These should ideally come from configuration or environment variables
            product_code = "GAS-FLEX-22-11-25"
            tariff_code = "G-1R-GAS-FLEX-22-11-25-B"
            
            # Construct the URL for the current rate
            url = f"{self.base_url}products/{product_code}/gas-tariffs/{tariff_code}/rates/"
            
            # Make the API request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Validate the response structure
            if 'results' not in data or not data['results']:
                logger.error("No gas rate results found in the response.")
                return None
            
            # Get the current UTC time to find the matching rate
            now_utc = datetime.now(timezone.utc)
            logger.debug(f"Current UTC time: {now_utc.isoformat()}")

            # Iterate through the rates to find the one that matches the current time
            for rate in data['results']:
                valid_from = rate.get('valid_from')
                valid_to = rate.get('valid_to')
                
                if not valid_from or not valid_to:
                    continue  # Skip if time information is incomplete
                
                # Parse the valid_from and valid_to times
                valid_from_dt = datetime.fromisoformat(valid_from.rstrip('Z')).replace(tzinfo=timezone.utc)
                valid_to_dt = datetime.fromisoformat(valid_to.rstrip('Z')).replace(tzinfo=timezone.utc)
                
                if valid_from_dt <= now_utc < valid_to_dt:
                    current_rate = rate.get('value_inc_vat')
                    logger.info(f"Current gas rate: {current_rate}p/kWh (Valid from {valid_from} to {valid_to})")
                    return current_rate
            
            # If no matching rate is found, log an error
            logger.error("No matching gas rate found for the current time.")
            return None

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching gas rate: {http_err} - Response: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection error occurred while fetching gas rate: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout error occurred while fetching gas rate: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request exception occurred while fetching gas rate: {req_err}")
        except ValueError as json_err:
            logger.error(f"JSON decoding failed: {json_err} - Response Content: {response.content}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching gas rate: {e}")
        
        return None