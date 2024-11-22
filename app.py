# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from heating_controller import SmartHeatingController, HeatingWindow
import sqlite3
import json

app = FastAPI(title="Smart Water Heating Control")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for production
app.mount("/static", StaticFiles(directory="static"), name="static")

# Models
class HeatingWindowCreate(BaseModel):
    start_time: str
    duration: int
    days: List[int]
    enabled: bool

class ModeUpdate(BaseModel):
    mode: str
    boost_duration: Optional[int] = None

# Routes
@app.get("/api/status")
async def get_status():
    """Get current system status."""
    try:
        status = controller.run()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/heating-windows")
async def get_heating_windows():
    """Get all configured heating windows."""
    return {"windows": controller.heating_windows}

@app.post("/api/heating-windows")
async def create_heating_window(window: HeatingWindowCreate):
    """Create a new heating window."""
    try:
        new_window = HeatingWindow(**window.dict())
        controller.add_heating_window(new_window)
        return {"message": "Window created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/mode")
async def update_mode(mode_update: ModeUpdate):
    """Update controller mode."""
    try:
        controller.set_mode(mode_update.mode, mode_update.boost_duration)
        return {"message": f"Mode updated to {mode_update.mode}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics."""
    return {
        "avg_duration": controller.get_average_heating_duration(),
        "savings": controller.get_cost_savings(),
        "current_month_costs": controller.get_cost_savings(30),
        "current_week_costs": controller.get_cost_savings(7)
    }

@app.get("/api/rates/history")
async def get_rate_history(days: int = 7):
    """Get historical electricity rates."""
    with sqlite3.connect(controller.DATABASE_PATH) as conn:
        cursor = conn.execute('''
            SELECT timestamp, rate 
            FROM electricity_rates 
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp
        ''', (days,))
        return {"rates": cursor.fetchall()}