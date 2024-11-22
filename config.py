# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class PropertyConfig:
    def __init__(self, name, electricity_mpan, electricity_serial, gas_mprn, gas_serial):
        self.name = name
        self.electricity_mpan = electricity_mpan
        self.electricity_serial = electricity_serial
        self.gas_mprn = gas_mprn
        self.gas_serial = gas_serial

# Define property configurations
BASEMENT = PropertyConfig(
    "37A",
    None,
    None,
    "2411062101",
    "E6S12559101961"
)

MAIN_HOUSE = PropertyConfig(
    "37",
    "1100024369080",
    "22J0669504",
    "2411062202",
    "E6S14573012361"
)

# API Keys
OCTOPUS_API_KEY = os.getenv('OCTOPUS_API_KEY')
WEATHER_LATITUDE = 52.2823
WEATHER_LONGITUDE = -1.5367

# Google Cloud / Nest Configuration
CLOUD_PROJECT_ID = "nest-optimization"  # Google Cloud project ID
NEST_PROJECT_ID = "dcd67c4f-e5a4-4636-86ff-254bb867742f"  # Device Access project ID
NEST_CLIENT_ID = "56513426026-ucnsa294ej8o8srm3ionco1e2lijr3cs.apps.googleusercontent.com"
NEST_CLIENT_SECRET = os.getenv('NEST_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8080/oauth2callback"  # Consistent Redirect URI
SCOPES = [
    "https://www.googleapis.com/auth/sdm.service"
]

# OAuth endpoints
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# Pub/Sub Configuration
PUBSUB_TOPIC = "projects/sdm-prod/topics/enterprise-dcd67c4f-e5a4-4636-86ff-254bb867742f"

# Octopus Configuration
AGILE_PRODUCT_CODE = 'AGILE-FLEX-22-11-25'
AGILE_TARIFF_CODE = 'E-1R-AGILE-FLEX-22-11-25-B'

# Temperature Settings
HOT_WATER_MAX_TEMP = float(os.getenv('HOT_WATER_MAX_TEMP', 60))
HOT_WATER_MIN_TEMP = float(os.getenv('HOT_WATER_MIN_TEMP', 50))
HEATING_MAX_TEMP = float(os.getenv('HEATING_MAX_TEMP', 21))
HEATING_MIN_TEMP = float(os.getenv('HEATING_MIN_TEMP', 18))

# Price Thresholds (p/kWh)
CHEAP_RATE_THRESHOLD = 15.0
EXPENSIVE_RATE_THRESHOLD = 25.0

# Time periods
PEAK_START = '16:00'
PEAK_END = '19:00'

# Application Settings
PORT = int(os.getenv('PORT', 8080))
DEBUG = os.getenv('DEBUG', 'False') == 'True'