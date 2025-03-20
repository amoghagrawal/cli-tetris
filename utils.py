import random
from constants import COLORS


def format_time(seconds):
    """
    Format time in seconds to mm:ss format
    
    Args:
        seconds (int): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def format_score(score):
    """
    Format score with thousands separators
    
    Args:
        score (int): The score to format
        
    Returns:
        str: Formatted score string
    """
    return f"{score:,}" 