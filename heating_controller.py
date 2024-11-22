# heating_controller.py
import logging
from datetime import datetime, timedelta
from typing import Dict
from octopus_client import OctopusClient
from config import (
    CHEAP_RATE_THRESHOLD,
    EXPENSIVE_RATE_THRESHOLD,
    PEAK_START,
    PEAK_END,
    HEATING_MAX_TEMP,
    HEATING_MIN_TEMP
)
from nest_client import NestClient

logger = logging.getLogger(__name__)

class SmartHeatingController:
    def __init__(self, property_config, nest_client):
        self.property_config = property_config
        self.octopus = OctopusClient()
        self.nest = nest_client
        self.last_adjustment = None
        self.rate_history = []
        logger.info(f"Initialized controller for property: {property_config.name}")
    
    def predict_rate_trend(self) -> float:
        """Calculate the trend in electricity rates."""
        if len(self.rate_history) < 3:
            return 0
        recent_rates = self.rate_history[-3:]
        trend = sum(b - a for a, b in zip(recent_rates[:-1], recent_rates[1:])) / 2
        return trend
            
    def get_optimal_temperature(self, current_rate: float, current_temp: float) -> float:
        """Calculate optimal temperature based on current conditions."""
        is_peak = self.is_peak_time()
        rate_trend = self.predict_rate_trend()
        
        min_temp = HEATING_MIN_TEMP
        max_temp = HEATING_MAX_TEMP
        
        # Reduce max temp during peak hours
        if is_peak:
            max_temp = min(max_temp, HEATING_MIN_TEMP + 1)
            logger.info(f"Peak time adjustment - reducing max temp to {max_temp}")
        
        # Adjust based on rate trend
        if rate_trend > 0:
            max_temp = min(max_temp, current_temp + 0.5)
            logger.info("Rising rate trend - limiting temperature increase")
        elif rate_trend < 0:
            min_temp = max(min_temp, current_temp - 0.5)
            logger.info("Falling rate trend - limiting temperature decrease")
            
        # Calculate target based on current rate
        rate_factor = (EXPENSIVE_RATE_THRESHOLD - current_rate) / (EXPENSIVE_RATE_THRESHOLD - CHEAP_RATE_THRESHOLD)
        rate_factor = max(0, min(1, rate_factor))
        
        target_temp = min_temp + (max_temp - min_temp) * rate_factor
        logger.info(f"Calculated optimal temperature: {target_temp}°C (rate factor: {rate_factor:.2f})")
        
        return round(target_temp, 1)

    def is_peak_time(self) -> bool:
        """Check if current time is during peak hours."""
        now = datetime.now().strftime('%H:%M')
        return PEAK_START <= now <= PEAK_END

    def should_update_temperature(self, current_temp: float, target_temp: float) -> bool:
        """Determine if temperature should be updated based on conditions."""
        if self.last_adjustment is None:
            return True
                
        time_since_last = datetime.now() - self.last_adjustment
        temp_diff = abs(current_temp - target_temp)
        
        if temp_diff > 2:
            return time_since_last > timedelta(minutes=10)
        elif temp_diff > 1:
            return time_since_last > timedelta(minutes=20)
        else:
            return time_since_last > timedelta(minutes=30)

    def run(self) -> Dict:
        """Execute the main control loop."""
        try:
            # Refresh Nest token if needed
            self.nest.refresh_token_if_needed()
            
            # Get current conditions
            current_rate = self.octopus.get_current_rate()
            current_temp = self.nest.get_current_temperature()
            is_peak = self.is_peak_time()
            
            logger.info(f"Current conditions - Rate: {current_rate}p/kWh, Temperature: {current_temp}°C, Peak time: {is_peak}")
            
            if current_rate is None or current_temp is None:
                logger.error("Failed to get current conditions")
                return {"success": False, "error": "Failed to get current conditions"}
            
            # Update rate history
            self.rate_history.append(current_rate)
            if len(self.rate_history) > 12:
                self.rate_history.pop(0)
            
            # Calculate target temperature
            target_temp = self.get_optimal_temperature(current_rate, current_temp)
            
            # Update temperature if needed
            if self.should_update_temperature(current_temp, target_temp):
                if self.nest.set_temperature(target_temp):
                    self.last_adjustment = datetime.now()
                    logger.info(f"Temperature adjusted to {target_temp}°C")
                else:
                    logger.error("Failed to set temperature")
            else:
                logger.info("Temperature update not needed at this time")
            
            # Update hot water based on rate
            is_cheap = current_rate < CHEAP_RATE_THRESHOLD
            self.nest.set_hot_water_state(is_cheap and not is_peak)
            
            return {
                "success": True,
                "current_rate": current_rate,
                "current_temp": current_temp,
                "target_temp": target_temp,
                "is_peak": is_peak,
                "is_cheap": is_cheap,
                "last_adjustment": self.last_adjustment
            }
            
        except Exception as e:
            logger.error(f"Error in control loop: {str(e)}")
            return {"success": False, "error": str(e)}