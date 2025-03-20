import os
import json
import time
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Union, Optional

from utils import format_score, format_time, backup_file

# Get logger
logger = logging.getLogger('tetris')

# Default location for high scores file
DEFAULT_SCORES_FILE = "tetris_scores.json"

# Maximum number of scores to keep
MAX_SCORES = 10


def load_high_scores(file_path: str = DEFAULT_SCORES_FILE) -> List[Dict[str, Union[int, float, str]]]:
    """
    Load high scores from a JSON file
    
    Args:
        file_path: Path to the high scores file
        
    Returns:
        List of high score entries
    """
    logger.debug(f"Loading high scores from {file_path}")
    
    if not os.path.exists(file_path):
        logger.info(f"High scores file {file_path} does not exist, returning empty list")
        return []
    
    try:
        with open(file_path, 'r') as f:
            scores = json.load(f)
        
        # Validate that scores is a list of dictionaries with required keys
        if not isinstance(scores, list):
            logger.warning(f"High scores file {file_path} does not contain a list, returning empty list")
            return []
        
        valid_scores = []
        for score in scores:
            if (isinstance(score, dict) and 
                'score' in score and 
                'level' in score and
                'lines' in score and
                'date' in score):
                valid_scores.append(score)
            else:
                logger.warning(f"Invalid score entry found in {file_path}: {score}")
        
        # Sort by score (highest first)
        valid_scores.sort(key=lambda x: x['score'], reverse=True)
        
        logger.debug(f"Loaded {len(valid_scores)} high scores from {file_path}")
        return valid_scores[:MAX_SCORES]
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from high scores file {file_path}: {e}")
        
        # Try to recover by using a backup file
        backup_path = f"{file_path}.bak"
        if os.path.exists(backup_path):
            logger.info(f"Attempting to recover from backup {backup_path}")
            try:
                with open(backup_path, 'r') as f:
                    scores = json.load(f)
                
                if isinstance(scores, list):
                    logger.info(f"Recovery successful, restoring from backup")
                    # Restore the backup as the main file
                    shutil.copy2(backup_path, file_path)
                    return scores[:MAX_SCORES]
            except Exception as recovery_error:
                logger.error(f"Recovery attempt failed: {recovery_error}")
        
        return []
    except IOError as e:
        logger.error(f"Error reading high scores file {file_path}: {e}")
        return []


def save_high_scores(scores: List[Dict[str, Union[int, float, str]]], 
                    file_path: str = DEFAULT_SCORES_FILE) -> bool:
    """
    Save high scores to a JSON file
    
    Args:
        scores: List of high score entries
        file_path: Path to the high scores file
        
    Returns:
        True if saved successfully, False otherwise
    """
    logger.debug(f"Saving {len(scores)} high scores to {file_path}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Back up the current file if it exists
        if os.path.exists(file_path):
            backup_file(file_path)
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only the highest scores
        scores = scores[:MAX_SCORES]
        
        # Use a temporary file to avoid corruption if the program crashes
        temp_file = f"{file_path}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(scores, f, indent=2)
        
        # Ensure the write is completed before renaming
        os.fsync(f.fileno())
        
        # Replace the original file
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_file, file_path)
        
        logger.info(f"Successfully saved {len(scores)} high scores to {file_path}")
        return True
    except IOError as e:
        logger.error(f"Error writing high scores file {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving high scores: {e}")
        return False


def add_high_score(score: int, level: int, lines: int, duration: float,
                  file_path: str = DEFAULT_SCORES_FILE) -> bool:
    """
    Add a new high score
    
    Args:
        score: Player's score
        level: Level reached
        lines: Lines cleared
        duration: Game duration in seconds
        file_path: Path to the high scores file
        
    Returns:
        True if score was added to high scores, False otherwise
    """
    logger.info(f"Adding high score: {score} points, level {level}, {lines} lines, {format_time(duration)} duration")
    
    try:
        scores = load_high_scores(file_path)
        
        # Add the new score
        new_score = {
            'score': score,
            'level': level,
            'lines': lines,
            'duration': duration,
            'date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        scores.append(new_score)
        
        # Sort and trim
        scores.sort(key=lambda x: x['score'], reverse=True)
        scores = scores[:MAX_SCORES]
        
        # Save to file
        return save_high_scores(scores, file_path)
    except Exception as e:
        logger.error(f"Error adding high score: {e}")
        return False


def is_high_score(score: int, file_path: str = DEFAULT_SCORES_FILE) -> bool:
    """
    Check if a score qualifies as a high score
    
    Args:
        score: Score to check
        file_path: Path to the high scores file
        
    Returns:
        True if this is a high score, False otherwise
    """
    try:
        scores = load_high_scores(file_path)
        
        # Any score is a high score if we have fewer than MAX_SCORES
        if len(scores) < MAX_SCORES:
            logger.debug(f"Score {score} qualifies as high score (fewer than {MAX_SCORES} scores)")
            return True
        
        # Otherwise, check if it's higher than the lowest score
        lowest_score = scores[-1]['score'] if scores else 0
        is_high = score > lowest_score
        
        if is_high:
            logger.debug(f"Score {score} qualifies as high score (higher than lowest score {lowest_score})")
        else:
            logger.debug(f"Score {score} does not qualify as high score (not higher than lowest score {lowest_score})")
            
        return is_high
    except Exception as e:
        logger.error(f"Error checking high score: {e}")
        # In case of error, assume it's a high score to avoid frustration
        return True


def format_high_scores(scores: List[Dict[str, Union[int, float, str]]]) -> List[str]:
    """
    Format high scores for display
    
    Args:
        scores: List of high score entries
        
    Returns:
        List of formatted strings
    """
    formatted = []
    
    try:
        for i, score in enumerate(scores):
            score_str = format_score(score.get('score', 0))
            level_str = str(score.get('level', 1))
            lines_str = str(score.get('lines', 0))
            
            # Format duration if present
            duration_str = ""
            if 'duration' in score:
                duration_str = format_time(score['duration'])
            
            # Format date
            date_str = score.get('date', 'Unknown')
            
            # Create the formatted string
            formatted.append(
                f"{i+1}. {score_str} - Level {level_str} - {lines_str} lines - {duration_str} - {date_str}"
            )
    except Exception as e:
        logger.error(f"Error formatting high scores: {e}")
        formatted.append("Error formatting high scores")
    
    return formatted


def reset_high_scores(file_path: str = DEFAULT_SCORES_FILE) -> bool:
    """
    Reset high scores by creating an empty scores file
    
    Args:
        file_path: Path to the high scores file
        
    Returns:
        True if successfully reset, False otherwise
    """
    try:
        # Backup the current file first
        if os.path.exists(file_path):
            backup_path = f"{file_path}.{int(time.time())}.bak"
            try:
                shutil.copy2(file_path, backup_path)
                logger.info(f"Backed up high scores to {backup_path} before reset")
            except Exception as e:
                logger.warning(f"Could not create backup before reset: {e}")
        
        # Create an empty scores file
        success = save_high_scores([], file_path)
        if success:
            logger.info(f"High scores reset successfully: {file_path}")
        return success
    except Exception as e:
        logger.error(f"Error resetting high scores: {e}")
        return False


def get_high_score_count(file_path: str = DEFAULT_SCORES_FILE) -> int:
    """
    Get the number of high scores in the file
    
    Args:
        file_path: Path to the high scores file
        
    Returns:
        Number of high scores
    """
    try:
        scores = load_high_scores(file_path)
        return len(scores)
    except Exception as e:
        logger.error(f"Error getting high score count: {e}")
        return 0 