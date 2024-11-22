# main.py
import schedule
import time
import logging
from heating_controller import SmartHeatingController
from config import MAIN_HOUSE, BASEMENT
from nest_client import NestClient

# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nest_octopus.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_controller(nest_client):
    try:
        # Run for both properties
        main_controller = SmartHeatingController(MAIN_HOUSE, nest_client)
        basement_controller = SmartHeatingController(BASEMENT, nest_client)
        
        main_result = main_controller.run()
        logger.info(f"Main house controller run complete: {main_result}")
        
        basement_result = basement_controller.run()
        logger.info(f"Basement controller run complete: {basement_result}")
    
    except Exception as e:
        logger.error(f"Error running controller: {e}")

def main():
    logger.info("Starting Smart Heating Controller")
    
    # Initialize Nest Client once
    try:
        nest_client = NestClient()
    except Exception as e:
        logger.error(f"Failed to initialize NestClient: {e}")
        return
    
    # Schedule regular checks every 30 minutes
    schedule.every(30).minutes.do(run_controller, nest_client=nest_client)
    
    # Initial run
    run_controller(nest_client)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()