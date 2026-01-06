"""Helper utilities for data generation."""
import uuid
import random
from typing import Optional, List


def generate_id() -> str:
    """Generate a UUID-style ID for entities.
    
    Returns:
        String UUID (without dashes to match Asana GID format)
    """
    return str(uuid.uuid4()).replace('-', '')


def weighted_choice(choices: List, weights: List[float]) -> any:
    """Make a weighted random choice.
    
    Args:
        choices: List of choices
        weights: List of weights (probabilities)
        
    Returns:
        Selected choice
    """
    return random.choices(choices, weights=weights, k=1)[0]


def random_subset(items: List, min_count: int = 0, max_count: Optional[int] = None) -> List:
    """Get a random subset of items.
    
    Args:
        items: List of items
        min_count: Minimum number of items
        max_count: Maximum number of items (default: len(items))
        
    Returns:
        Random subset of items
    """
    if max_count is None:
        max_count = len(items)
    count = random.randint(min_count, min(max_count, len(items)))
    return random.sample(items, count)

