"""
Utility functions for time calculations.
"""

from datetime import datetime
from typing import Tuple


def calculate_worked_hours(clock_in: str) -> float:
    """
    Calculate hours worked since clock in time.
    
    Args:
        clock_in: Clock in time in HH:MM format
        
    Returns:
        Hours worked as a float
    """
    clock_in_time = datetime.strptime(clock_in, "%H:%M")
    now = datetime.now()
    current_time = now.replace(hour=now.hour, minute=now.minute, second=0, microsecond=0)
    
    worked_minutes = (current_time.hour * 60 + current_time.minute) - \
                     (clock_in_time.hour * 60 + clock_in_time.minute)
    
    return worked_minutes / 60


def calculate_remaining_hours(clock_in: str, workday_hours: int = 8) -> float:
    """
    Calculate remaining hours in workday.
    
    Args:
        clock_in: Clock in time in HH:MM format
        workday_hours: Total hours in a workday (default: 8)
        
    Returns:
        Remaining hours (negative if overtime)
    """
    worked_hours = calculate_worked_hours(clock_in)
    return workday_hours - worked_hours


def format_remaining_time(hours: float) -> Tuple[int, int]:
    """
    Format remaining hours into hours and minutes.
    
    Args:
        hours: Hours as float
        
    Returns:
        Tuple of (hours, minutes)
    """
    h = int(hours)
    m = int((hours - h) * 60)
    return (h, m)


def format_time_display(hours: int, minutes: int) -> str:
    """
    Format hours and minutes for display.
    
    Args:
        hours: Hours
        minutes: Minutes
        
    Returns:
        Formatted string (e.g., "6h 23m", "45m")
    """
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
