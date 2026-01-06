"""Date and time generation utilities."""
import random
from datetime import datetime, timedelta
from typing import Optional, List
import numpy as np


def random_date(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random date between start and end dates.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        
    Returns:
        Random datetime between start and end
    """
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)


def random_weekday_date(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random weekday (Monday-Friday) between dates.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        
    Returns:
        Random weekday datetime
    """
    date = random_date(start_date, end_date)
    # Adjust if weekend
    while date.weekday() >= 5:  # Saturday=5, Sunday=6
        if date < end_date - timedelta(days=2):
            date += timedelta(days=1)
        else:
            date -= timedelta(days=1)
    return date


def generate_due_date(created_at: datetime, end_date: datetime, 
                     distribution: str = "realistic") -> Optional[datetime]:
    """Generate a realistic due date based on creation date.
    
    Distribution based on research:
    - 25% within 1 week
    - 40% within 1 month
    - 20% 1-3 months out
    - 10% no due date
    - 5% overdue
    
    Args:
        created_at: Task creation datetime
        end_date: Maximum date (end of simulation period)
        distribution: Distribution type ("realistic" or "uniform")
        
    Returns:
        Due date or None (for 10% without due dates)
    """
    if distribution == "realistic":
        rand = random.random()
        if rand < 0.10:  # 10% no due date
            return None
        elif rand < 0.35:  # 25% within 1 week
            days_ahead = random.randint(1, 7)
        elif rand < 0.75:  # 40% within 1 month
            days_ahead = random.randint(8, 30)
        elif rand < 0.95:  # 20% 1-3 months
            days_ahead = random.randint(31, 90)
        else:  # 5% overdue (before creation)
            days_ahead = random.randint(-14, -1)
    else:
        # Uniform distribution
        days_ahead = random.randint(1, 90)
    
    due_date = created_at + timedelta(days=days_ahead)
    
    # Ensure due date is within simulation period
    if due_date > end_date:
        due_date = end_date
    elif due_date < created_at - timedelta(days=30):
        due_date = created_at + timedelta(days=1)
    
    # 85% of due dates are on weekdays
    if random.random() < 0.85:
        while due_date.weekday() >= 5:
            due_date -= timedelta(days=1)
    
    return due_date


def generate_completion_date(created_at: datetime, due_date: Optional[datetime], 
                            completed: bool, end_date: datetime) -> Optional[datetime]:
    """Generate completion date for a task.
    
    Based on cycle time benchmarks: 1-14 days after creation (log-normal distribution).
    
    Args:
        created_at: Task creation datetime
        due_date: Task due date (if any)
        completed: Whether task is completed
        end_date: Maximum date (end of simulation period)
        
    Returns:
        Completion datetime or None if not completed
    """
    if not completed:
        return None
    
    # Log-normal distribution for cycle time (1-14 days)
    cycle_days = max(1, int(np.random.lognormal(mean=2.0, sigma=0.8)))
    cycle_days = min(cycle_days, 60)  # Cap at 60 days
    
    completed_at = created_at + timedelta(days=cycle_days)
    
    # Must be after creation and before end_date
    if completed_at < created_at:
        completed_at = created_at + timedelta(days=1)
    if completed_at > end_date:
        completed_at = end_date
    
    # If due date exists, completion is often near due date (but can be before or after)
    if due_date:
        if random.random() < 0.7:  # 70% complete near due date
            variance = random.randint(-3, 7)  # Can complete 3 days early to 7 days late
            completed_at = due_date + timedelta(days=variance)
            completed_at = max(completed_at, created_at + timedelta(days=1))
            completed_at = min(completed_at, end_date)
    
    return completed_at


def generate_creation_times(start_date: datetime, end_date: datetime, 
                           count: int) -> List[datetime]:
    """Generate realistic creation times with higher activity on Mon-Wed.
    
    Args:
        start_date: Start of simulation period
        end_date: End of simulation period
        count: Number of timestamps to generate
        
    Returns:
        List of datetime objects
    """
    times = []
    time_span = (end_date - start_date).total_seconds()
    
    for _ in range(count):
        # Higher creation rates Mon-Wed
        random_seconds = random.randint(0, int(time_span))
        dt = start_date + timedelta(seconds=random_seconds)
        
        # Adjust weight based on weekday
        if dt.weekday() < 3:  # Mon-Wed
            if random.random() > 0.3:  # 70% keep, 30% might shift
                pass
        elif dt.weekday() >= 5:  # Weekend
            if random.random() > 0.2:  # 80% shift to weekday
                days_to_add = (7 - dt.weekday()) % 7
                if days_to_add == 0:
                    days_to_add = 1
                dt += timedelta(days=days_to_add)
                if dt > end_date:
                    dt -= timedelta(days=7)
        
        times.append(dt)
    
    times.sort()
    return times

