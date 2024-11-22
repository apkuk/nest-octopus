import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_octopus_connection():
    # Get API key from environment variables
    api_key = os.getenv('OCTOPUS_API_KEY')
    
    # Set up time parameters
    now = datetime.utcnow()
    period_from = now.strftime("%Y-%m-%dT%H:%M:00Z")
    period_to = (now + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:00Z")
    
    # Make API request
    url = "https://api.octopus.energy/v1/products/AGILE-FLEX-22-11-25/electricity-tariffs/E-1R-AGILE-FLEX-22-11-25-C/standard-unit-rates/"
    params = {
        'period_from': period_from,
        'period_to': period_to
    }
    
    try:
        response = requests.get(url, auth=(api_key, ''), params=params)
        response.raise_for_status()
        rates = response.json()['results']
        
        print("\nConnection successful! Current Agile rates:")
        print("-" * 50)
        for rate in rates[:3]:  # Show first 3 rates
            time = datetime.strptime(rate['valid_from'], "%Y-%m-%dT%H:%M:%SZ")
            print(f"Time: {time.strftime('%H:%M')} - Price: {rate['value_inc_vat']:.2f}p/kWh")
            
    except Exception as e:
        print(f"Error connecting to Octopus API: {str(e)}")

if __name__ == "__main__":
    test_octopus_connection()