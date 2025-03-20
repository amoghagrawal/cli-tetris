import os
import json
import logging
import platform
from typing import Dict, Any, Optional
from pathlib import Path

# Get logger
logger = logging.getLogger('tetris')

# Default configuration file location
DEFAULT_CONFIG_FILE = "tetris_config.json"

# Default key bindings
DEFAULT_CONTROLS = {
    'move_left': ['left', 'a', 'j'],
    'move_right': ['right', 'd', 'l'],
    'move_down': ['down', 's', 'i'],
    'rotate': ['up', 'w', 'k'],
    'hard_drop': ['space'],
    'hold': ['h', 'c'],
    'pause': ['p'],
    'quit': ['q', 'escape'],
    'restart': ['r']
}

# Platform-specific key adjustments
if platform.system() == "Windows":
    DEFAULT_CONTROLS['quit'].append('ctrl+c')
elif platform.system() == "Darwin":  # macOS
    DEFAULT_CONTROLS['hard_drop'].append('cmd+space')
    DEFAULT_CONTROLS['quit'].append('cmd+q')

# Difficulty presets
DIFFICULTY_PRESETS = {
    'easy': {
        'initial_speed': 1.2,  # Slower initial speed
        'speed_increase': 0.0003,  # Slower speed increase
        'level_speed_increase': 0.08,
        'lines_per_level': 12  # More lines needed to level up
    },
    'normal': {
        'initial_speed': 1.0,
        'speed_increase': 0.0005,
        'level_speed_increase': 0.1,
        'lines_per_level': 10
    },
    'hard': {
        'initial_speed': 0.8,  # Faster initial speed
        'speed_increase': 0.0008,  # Faster speed increase
        'level_speed_increase': 0.12,
        'lines_per_level': 8  # Fewer lines needed to level up
    },
    'expert': {
        'initial_speed': 0.6,
        'speed_increase': 0.001,
        'level_speed_increase': 0.15,
        'lines_per_level': 6
    }
}


def get_config_path(file_path: Optional[str] = None) -> str:
    """
    Get the configuration file path, creating necessary directories
    
    Args:
        file_path: Optional path to configuration file
        
    Returns:
        Path to configuration file
    """
    if file_path:
        path = Path(file_path)
    else:
        # Use platform-specific config directory
        if platform.system() == "Windows":
            app_data = os.environ.get('APPDATA', '')
            if app_data:
                path = Path(app_data) / "TetrisCLI" / DEFAULT_CONFIG_FILE
            else:
                path = Path(DEFAULT_CONFIG_FILE)
        elif platform.system() == "Darwin":  # macOS
            path = Path.home() / "Library" / "Application Support" / "TetrisCLI" / DEFAULT_CONFIG_FILE
        else:  # Linux and others
            xdg_config = os.environ.get('XDG_CONFIG_HOME', '')
            if xdg_config:
                path = Path(xdg_config) / "tetris" / DEFAULT_CONFIG_FILE
            else:
                path = Path.home() / ".config" / "tetris" / DEFAULT_CONFIG_FILE
    
    # Create directory if it doesn't exist
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        logger.warning(f"Permission denied creating config directory at {path.parent}, falling back to current directory")
        path = Path(DEFAULT_CONFIG_FILE)
    except Exception as e:
        logger.error(f"Error creating config directory: {e}")
        path = Path(DEFAULT_CONFIG_FILE)
    
    logger.debug(f"Using config path: {path}")
    return str(path)


def load_config(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a JSON file
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    default_config = {
        'controls': DEFAULT_CONTROLS,
        'difficulty': 'normal',
        'high_scores_file': 'tetris_scores.json',
        'fullscreen': False,
        'terminal_size': [80, 24]
    }
    
    # Get proper config path
    config_path = get_config_path(file_path)
    
    if not os.path.exists(config_path):
        logger.info(f"Config file {config_path} does not exist, using defaults")
        # Create the default config file for future use
        try:
            save_config(default_config, config_path)
        except Exception as e:
            logger.warning(f"Failed to create default config file: {e}")
        return default_config
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.debug(f"Loaded configuration from {config_path}")
        
        # Merge with default config to ensure all keys exist
        merged_config = default_config.copy()
        
        # Update with loaded values
        for key, value in config.items():
            if key in merged_config:
                merged_config[key] = value
        
        # Validate controls
        if 'controls' in config:
            # Make sure all required controls are present
            for control in DEFAULT_CONTROLS:
                if control not in merged_config['controls'] or not merged_config['controls'][control]:
                    logger.warning(f"Missing required control '{control}', using default")
                    merged_config['controls'][control] = DEFAULT_CONTROLS[control]
        
        # Validate difficulty
        if merged_config['difficulty'] not in DIFFICULTY_PRESETS:
            logger.warning(f"Invalid difficulty '{merged_config['difficulty']}', using 'normal'")
            merged_config['difficulty'] = 'normal'
        
        return merged_config
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from config file {config_path}: {e}")
        return default_config
    except IOError as e:
        logger.error(f"Error reading config file {config_path}: {e}")
        return default_config
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}")
        return default_config


def save_config(config: Dict[str, Any], file_path: Optional[str] = None) -> bool:
    """
    Save configuration to a JSON file
    
    Args:
        config: Configuration dictionary
        file_path: Path to the configuration file
        
    Returns:
        True if saved successfully, False otherwise
    """
    # Get proper config path
    config_path = get_config_path(file_path)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        # Backup existing config if it exists
        if os.path.exists(config_path):
            try:
                import shutil
                backup_path = f"{config_path}.bak"
                shutil.copy2(config_path, backup_path)
                logger.debug(f"Created backup of config file to {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create backup of config file: {e}")
        
        # Write to a temporary file first
        temp_path = f"{config_path}.tmp"
        with open(temp_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Ensure the write is completed
        os.fsync(f.fileno())
        
        # Replace the original file
        if os.path.exists(config_path):
            os.remove(config_path)
        os.rename(temp_path, config_path)
        
        logger.debug(f"Saved configuration to {config_path}")
        return True
    except PermissionError as e:
        logger.error(f"Permission denied saving config file {config_path}: {e}")
        return False
    except IOError as e:
        logger.error(f"Error writing config file {config_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error saving config: {e}")
        return False


def is_valid_key_for_action(key: str, action: str, config: Dict[str, Any]) -> bool:
    """
    Check if a key is valid for the given action
    
    Args:
        key: Key to check
        action: Action to check for
        config: Configuration dictionary
        
    Returns:
        True if key is valid for action, False otherwise
    """
    try:
        if key is None or action is None:
            return False
            
        valid = action in config['controls'] and key in config['controls'][action]
        return valid
    except Exception as e:
        logger.error(f"Error checking key validity: {e}")
        return False


def get_key_map(config: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    Get a key map dictionary for use with translate_key function
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Key mapping dictionary
    """
    if config is None:
        config = load_config()
    
    try:
        # Create a mapping from key to action
        key_map = {}
        controls = config.get('controls', DEFAULT_CONTROLS)
        
        for action, keys in controls.items():
            for key in keys:
                # Convert action to control key
                if action == 'move_left':
                    key_map[key] = 'left'
                elif action == 'move_right':
                    key_map[key] = 'right'
                elif action == 'move_down':
                    key_map[key] = 'down'
                elif action == 'rotate':
                    key_map[key] = 'up'
                elif action == 'hard_drop':
                    key_map[key] = 'space'
                else:  # Other keys pass through (pause, quit, etc.)
                    key_map[key] = key
        
        # Add platform-specific keys
        if platform.system() == "Windows":
            # Add Windows-specific key mappings
            key_map.update({
                'esc': 'escape',
                'enter': 'return'
            })
        elif platform.system() == "Darwin":  # macOS
            # Add macOS-specific key mappings
            key_map.update({
                'return': 'enter'
            })
            
        return key_map
    except Exception as e:
        logger.error(f"Error creating key map: {e}")
        # Return a basic map as fallback
        return {k: k for k in 'abcdefghijklmnopqrstuvwxyz'}


def get_difficulty_settings(difficulty: str) -> Dict[str, Any]:
    """
    Get game settings for the specified difficulty
    
    Args:
        difficulty: Difficulty level name
        
    Returns:
        Dictionary of game settings
    """
    if not difficulty:
        logger.warning("Empty difficulty provided, using 'normal'")
        difficulty = 'normal'
        
    # Default to normal if difficulty not found
    if difficulty not in DIFFICULTY_PRESETS:
        logger.warning(f"Unknown difficulty '{difficulty}', using 'normal'")
        difficulty = 'normal'
    
    logger.debug(f"Using difficulty settings for '{difficulty}'")
    return DIFFICULTY_PRESETS[difficulty]


def reset_config() -> bool:
    """
    Reset configuration to defaults
    
    Returns:
        True if reset successfully, False otherwise
    """
    try:
        # Get proper config path
        config_path = get_config_path()
        
        # Create default config
        default_config = {
            'controls': DEFAULT_CONTROLS,
            'difficulty': 'normal',
            'high_scores_file': 'tetris_scores.json',
            'fullscreen': False,
            'terminal_size': [80, 24]
        }
        
        # Save default config
        success = save_config(default_config, config_path)
        if success:
            logger.info(f"Configuration reset to defaults")
        return success
    except Exception as e:
        logger.error(f"Error resetting configuration: {e}")
        return False 