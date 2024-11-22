# heating_controller.py
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import sqlite3
from octopus_client import OctopusClient
from config import (
    CHEAP_RATE_THRESHOLD,
    EXPENSIVE_RATE_THRESHOLD,
    PEAK_START,
    PEAK_END,
    DATABASE_PATH
)

logger = logging.getLogger(__name__)

@dataclass
class HeatingWindow:
    start_time: str  # HH:MM format
    duration: int    # Minutes
    days: List[int]  # 0-6 (Monday-Sunday)
    enabled: bool

@dataclass
class HeatingSession:
    start_time: datetime
    end_time: Optional[datetime]
    rate: float
    completed: bool

class SmartHeatingController:
    def __init__(self, property_config, nest_client):
        self.property_config = property_config
        self.octopus = OctopusClient()
        self.nest = nest_client
        self.heating_windows = []
        self.current_session = None
        self.mode = "optimized"  # optimized, boost, off
        self.boost_end_time = None
        self._init_database()
        logger.info(f"Initialized controller for property: {property_config.name}")
    
    def _init_database(self):
        """Initialize SQLite database for storing historical data."""
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS heating_sessions (
                    id INTEGER PRIMARY KEY,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER,
                    rate REAL,
                    cost REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS electricity_rates (
                    timestamp TIMESTAMP PRIMARY KEY,
                    rate REAL
                )
            ''')
    
    def log_heating_session(self, session: HeatingSession):
        """Log completed heating session to database."""
        if not session.completed or not session.end_time:
            return
            
        duration = (session.end_time - session.start_time).total_seconds() / 60
        cost = (duration / 60) * session.rate * 3  # 3kW immersion heater
        
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('''
                INSERT INTO heating_sessions 
                (start_time, end_time, duration_minutes, rate, cost)
                VALUES (?, ?, ?, ?, ?)
            ''', (session.start_time, session.end_time, duration, session.rate, cost))
    
    def log_electricity_rate(self, timestamp: datetime, rate: float):
        """Log electricity rate to database."""
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO electricity_rates (timestamp, rate)
                VALUES (?, ?)
            ''', (timestamp, rate))
    
    def get_average_heating_duration(self, days: int = 7) -> float:
        """Get average heating duration over specified days."""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute('''
                SELECT AVG(duration_minutes) FROM heating_sessions
                WHERE start_time >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            result = cursor.fetchone()[0]
            return result if result else 60  # Default 60 minutes
    
    def get_cost_savings(self, period_days: int = 30) -> Dict:
        """Calculate cost savings compared to peak rates."""
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.execute('''
                SELECT 
                    SUM(duration_minutes * rate / 60) as actual_cost,
                    SUM(duration_minutes / 60) as total_hours
                FROM heating_sessions
                WHERE start_time >= datetime('now', '-' || ? || ' days')
            ''', (period_days,))
            result = cursor.fetchone()
            if not result or not result[0]:
                return {"savings": 0, "actual_cost": 0, "peak_cost": 0}
                
            actual_cost = result[0]
            total_hours = result[1]
            peak_cost = total_hours * EXPENSIVE_RATE_THRESHOLD
            
            return {
                "savings": peak_cost - actual_cost,
                "actual_cost": actual_cost,
                "peak_cost": peak_cost
            }

    def set_mode(self, mode: str, boost_duration: int = 0):
        """Set controller mode (optimized, boost, off)."""
        self.mode = mode
        if mode == "boost" and boost_duration:
            self.boost_end_time = datetime.now() + timedelta(minutes=boost_duration)
        elif mode != "boost":
            self.boost_end_time = None
    
    def add_heating_window(self, window: HeatingWindow):
        """Add a new heating window."""
        self.heating_windows.append(window)
    
    def is_peak_time(self) -> bool:
        """Check if current time is during peak hours."""
        now = datetime.now().strftime('%H:%M')
        return PEAK_START <= now <= PEAK_END

    def should_heat_water(self, current_rate: float) -> bool:
        """Determine if water should be heated based on current conditions."""
        now = datetime.now()
        
        # Check mode
        if self.mode == "off":
            return False
        elif self.mode == "boost":
            return now < self.boost_end_time if self.boost_end_time else False
        
        # Optimized mode
        if self.is_peak_time():
            return False
            
        # Check scheduled windows
        current_weekday = now.weekday()
        current_time = now.strftime('%H:%M')
        for window in self.heating_windows:
            if not window.enabled:
                continue
            if current_weekday in window.days:
                window_end = datetime.strptime(window.start_time, '%H:%M') + timedelta(minutes=window.duration)
                window_end_str = window_end.strftime('%H:%M')
                if window.start_time <= current_time <= window_end_str:
                    return True
        
        # Dynamic rate-based decision
        return current_rate < CHEAP_RATE_THRESHOLD

    def run(self) -> Dict:
        """Execute the main control loop."""
        try:
            # Refresh Nest token if needed
            self.nest.refresh_token_if_needed()
            
            # Get current rate
            current_rate = self.octopus.get_current_rate()
            if current_rate is None:
                logger.error("Failed to get current rate")
                return {"success": False, "error": "Failed to get current rate"}
            
            # Log electricity rate
            self.log_electricity_rate(datetime.now(), current_rate)
            
            # Determine if we should heat water
            should_heat = self.should_heat_water(current_rate)
            is_peak = self.is_peak_time()
            
            # Handle heating session tracking
            if should_heat and not self.current_session:
                self.current_session = HeatingSession(
                    start_time=datetime.now(),
                    end_time=None,
                    rate=current_rate,
                    completed=False
                )
            elif not should_heat and self.current_session:
                self.current_session.end_time = datetime.now()
                self.current_session.completed = True
                self.log_heating_session(self.current_session)
                self.current_session = None
            
            # Control hot water
            self.nest.set_hot_water_state(should_heat)
            
            return {
                "success": True,
                "current_rate": current_rate,
                "mode": self.mode,
                "is_heating": should_heat,
                "is_peak": is_peak,
                "boost_remaining": (self.boost_end_time - datetime.now()).total_seconds() / 60 if self.boost_end_time else 0,
                "avg_heating_duration": self.get_average_heating_duration(),
                "cost_savings": self.get_cost_savings()
            }
            
        except Exception as e:
            logger.error(f"Error in control loop: {str(e)}")
            return {"success": False, "error": str(e)}