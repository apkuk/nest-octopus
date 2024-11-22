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
        self.base_url = "https://api.octopus.energy/v1"  # Removed trailing slash
        
    def get_current_rate(self):
        """
        Fetch the current electricity rate.
        
        Returns:
            float: The current electricity rate in pence per kWh.
            None: If there was an error fetching the rate.
        """
        try:
            # Define the product and tariff codes
            product_code = "AGILE-FLEX-22-11-25"
            tariff_code = "E-1R-AGILE-FLEX-22-11-25-B"
            
            # Construct the URL for the current rate using standard-unit-rates
            url = f"{self.base_url}/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/"
            
            # Make the API request with basic auth instead of headers
            response = requests.get(
                url,
                auth=(self.api_key, ''),  # Octopus API uses Basic Auth
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Validate the response structure
            if 'results' not in data or not data['results']:
                logger.error("No rate results found in the response.")
                return None
            
            # Get the current UTC time
            now_utc = datetime.now(timezone.utc)
            logger.debug(f"Current UTC time: {now_utc.isoformat()}")

            # Iterate through the rates to find the one that matches the current time
            for rate in data['results']:
                valid_from = rate.get('valid_from')
                valid_to = rate.get('valid_to')
                
                if not valid_from or not valid_to:
                    continue
                
                # Parse the valid_from and valid_to times
                valid_from_dt = datetime.fromisoformat(valid_from.rstrip('Z')).replace(tzinfo=timezone.utc)
                valid_to_dt = datetime.fromisoformat(valid_to.rstrip('Z')).replace(tzinfo=timezone.utc)
                
                if valid_from_dt <= now_utc < valid_to_dt:
                    current_rate = rate.get('value_inc_vat')
                    logger.info(f"Current electricity rate: {current_rate}p/kWh (Valid from {valid_from} to {valid_to})")
                    return current_rate
            
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

    def get_consumption(self, mpan, serial, period_from=None, period_to=None):
        """
        Fetch electricity consumption data.
        
        Args:
            mpan: The MPAN number
            serial: The meter serial number
            period_from: Start date (optional)
            period_to: End date (optional)
            
        Returns:
            dict: Consumption data
            None: If there was an error
        """
        try:
            url = f"{self.base_url}/electricity-meter-points/{mpan}/meters/{serial}/consumption/"
            
            params = {}
            if period_from:
                params['period_from'] = period_from
            if period_to:
                params['period_to'] = period_to
                
            response = requests.get(
                url,
                auth=(self.api_key, ''),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching consumption data: {e}")
            return None

    def get_gas_consumption(self, mprn, serial, period_from=None, period_to=None):
        """
        Fetch gas consumption data.
        
        Args:
            mprn: The MPRN number
            serial: The meter serial number
            period_from: Start date (optional)
            period_to: End date (optional)
            
        Returns:
            dict: Consumption data
            None: If there was an error
        """
        try:
            url = f"{self.base_url}/gas-meter-points/{mprn}/meters/{serial}/consumption/"
            
            params = {}
            if period_from:
                params['period_from'] = period_from
            if period_to:
                params['period_to'] = period_to
                
            response = requests.get(
                url,
                auth=(self.api_key, ''),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching gas consumption data: {e}")
            return None