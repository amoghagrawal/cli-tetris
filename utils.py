import os
import sys
import time
import platform
import logging
from typing import Tuple, Dict, Any, Optional, List, Callable

logger = logging.getLogger('tetris')

# Try to import shutil for terminal size detection
try:
    import shutil
    SHUTIL_AVAILABLE = True
except ImportError:
    SHUTIL_AVAILABLE = False
    logger.warning("shutil module not available, falling back to alternative terminal size detection")

# Define OS-specific constants
WINDOWS = platform.system() == "Windows"
MACOS = platform.system() == "Darwin"
LINUX = platform.system() == "Linux"

logger.info(f"Platform detected: {platform.system()} ({platform.release()})")


def get_terminal_size() -> Tuple[int, int]:
    """
    Get the current terminal size (width, height) in characters.
    
    Returns:
        Tuple[int, int]: Width and height of terminal in characters
    """
    # Try using shutil (most reliable cross-platform)
    if SHUTIL_AVAILABLE:
        try:
            columns, lines = shutil.get_terminal_size()
            logger.debug(f"Terminal size detected with shutil: {columns}x{lines}")
            return columns, lines
        except Exception as e:
            logger.warning(f"Failed to get terminal size with shutil: {e}")
    
    # Fallback for Windows
    if WINDOWS:
        try:
            from ctypes import windll, create_string_buffer
            h = windll.kernel32.GetStdHandle(-11)
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
            if res:
                import struct
                left, top, right, bottom = struct.unpack('4H', csbi.raw[6:14])
                width = right - left + 1
                height = bottom - top + 1
                logger.debug(f"Terminal size detected with Win32 API: {width}x{height}")
                return width, height
            else:
                logger.warning("GetConsoleScreenBufferInfo failed")
        except (ImportError, AttributeError, OSError) as e:
            logger.warning(f"Failed to get terminal size with Win32 API: {e}")
    
    # Fallback for Unix/Linux/Mac
    try:
        import fcntl
        import termios
        import struct
        
        # Try STDOUT first
        try:
            fd = sys.stdout.fileno()
            dimensions = struct.unpack('HHHH', 
                fcntl.ioctl(fd, termios.TIOCGWINSZ, b'\0\0\0\0\0\0\0\0'))
            height, width = dimensions[0], dimensions[1]
            if width and height:
                logger.debug(f"Terminal size detected with ioctl: {width}x{height}")
                return width, height
        except (IOError, AttributeError) as e:
            logger.warning(f"Failed to get terminal size with ioctl: {e}")
            
        # Try environment variables
        try:
            width = int(os.environ.get('COLUMNS', 0))
            height = int(os.environ.get('LINES', 0))
            if width and height:
                logger.debug(f"Terminal size detected from environment: {width}x{height}")
                return width, height
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to get terminal size from environment: {e}")
    except (ImportError, IOError) as e:
        logger.warning(f"Failed to import Unix terminal modules: {e}")
    
    # Default fallback
    logger.warning("Using default terminal size: 80x24")
    return 80, 24


def set_terminal_size(width: int, height: int) -> bool:
    """
    Attempt to set the terminal size.
    
    Args:
        width: Desired width in characters
        height: Desired height in characters
        
    Returns:
        bool: True if successful, False otherwise
    """
    if width <= 0 or height <= 0:
        logger.error(f"Invalid terminal dimensions: {width}x{height}")
        return False
        
    if WINDOWS:
        try:
            result = os.system(f'mode con: cols={width} lines={height}')
            success = result == 0
            if success:
                logger.info(f"Set terminal size to {width}x{height} with mode command")
            else:
                logger.warning(f"Failed to set terminal size with mode command (exit code {result})")
            return success
        except Exception as e:
            logger.error(f"Error setting terminal size on Windows: {e}")
            return False
    elif LINUX or MACOS:
        try:
            # Approach 1: Using ANSI escape sequences
            sys.stdout.write(f"\x1b[8;{height};{width}t")
            sys.stdout.flush()
            logger.info(f"Set terminal size to {width}x{height} with ANSI escape sequence")
            
            # Validate the size was set correctly
            time.sleep(0.1)  # Give terminal time to resize
            actual_width, actual_height = get_terminal_size()
            if abs(actual_width - width) > 5 or abs(actual_height - height) > 5:
                logger.warning(f"Terminal resize may not have worked. Requested: {width}x{height}, got: {actual_width}x{actual_height}")
            
            return True
        except Exception as e:
            logger.error(f"Error setting terminal size on {platform.system()}: {e}")
            return False
    
    logger.warning(f"Terminal resizing not supported on {platform.system()}")
    return False


def is_terminal_size_sufficient(min_width: int = 80, min_height: int = 24) -> bool:
    """
    Check if the terminal size is sufficient for the game.
    
    Args:
        min_width: Minimum required width
        min_height: Minimum required height
        
    Returns:
        bool: True if terminal is large enough
    """
    width, height = get_terminal_size()
    sufficient = width >= min_width and height >= min_height
    
    if not sufficient:
        logger.warning(f"Terminal size insufficient: {width}x{height}, minimum required: {min_width}x{min_height}")
    
    return sufficient


def translate_key(key: str, key_map: Optional[Dict[str, str]] = None) -> str:
    """
    Translate a key using the provided key map or default.
    Useful for handling different keyboard layouts.
    
    Args:
        key: The key to translate
        key_map: Optional custom key mapping
        
    Returns:
        str: The translated key
    """
    if key is None:
        logger.warning("Received None key in translate_key")
        return ""
        
    default_map = {
        # Some common key translations for different layouts
        'a': 'left',      # For WASD controls
        'd': 'right',
        's': 'down',
        'w': 'up',
        'j': 'left',      # For Vim-style controls
        'l': 'right',
        'k': 'up',
        'i': 'down',
        ' ': 'space',
    }
    
    # Handle platform-specific key translations
    if WINDOWS:
        # Map Windows virtual key codes if needed
        pass
    elif MACOS:
        # Map Mac-specific keys if needed
        pass
    
    # Use custom map if provided, otherwise use default
    mapping = key_map if key_map else default_map
    
    try:
        # Return the mapped key or the original if not in map
        result = mapping.get(key.lower(), key)
        return result
    except (AttributeError, TypeError) as e:
        logger.error(f"Error translating key '{key}': {e}")
        return key


def create_fps_limiter(fps: int = 60) -> Callable[[], float]:
    """
    Create a function that limits execution to a specified FPS.
    
    Args:
        fps: Frames per second target
        
    Returns:
        callable: A function that sleeps to maintain FPS
    """
    try:
        frame_time = 1.0 / fps
        last_time = time.time()
        
        def limit_fps() -> float:
            """
            Sleep to maintain the desired FPS.
            
            Returns:
                float: Actual FPS achieved
            """
            nonlocal last_time
            current_time = time.time()
            elapsed = current_time - last_time
            
            # Sleep if we're running too fast
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
                
            # Calculate actual FPS
            actual_elapsed = time.time() - last_time
            last_time = time.time()
            actual_fps = 1.0 / actual_elapsed if actual_elapsed > 0 else 0
            
            if actual_fps < fps * 0.75:
                logger.debug(f"FPS drop detected: target={fps}, actual={actual_fps:.1f}")
                
            return actual_fps
            
        logger.debug(f"Created FPS limiter with target {fps} FPS")
        return limit_fps
    except Exception as e:
        logger.error(f"Error creating FPS limiter: {e}")
        # Return a dummy function as fallback
        return lambda: 0.0


def safe_color_blend(color1: str, color2: str, ratio: float = 0.5) -> str:
    """
    Safely blend two hex colors.
    
    Args:
        color1: First hex color (format: '#RRGGBB')
        color2: Second hex color (format: '#RRGGBB')
        ratio: Blend ratio (0.0 = color1, 1.0 = color2)
        
    Returns:
        str: Blended hex color
    """
    try:
        # Remove '#' if present
        c1 = color1.lstrip('#')
        c2 = color2.lstrip('#')
        
        # Validate hex colors
        if not (len(c1) == 6 and len(c2) == 6):
            logger.warning(f"Invalid hex color format: {color1} or {color2}")
            return color1  # Return first color as fallback
            
        # Convert to RGB
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
        
        # Ensure ratio is between 0 and 1
        ratio = max(0, min(1, ratio))
        
        # Blend
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    except Exception as e:
        logger.error(f"Error blending colors {color1} and {color2}: {e}")
        return color1  # Return first color as fallback


def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    try:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting time: {e}")
        return "00:00"


def format_score(score: int) -> str:
    """
    Format score with thousand separators.
    
    Args:
        score: The score to format
        
    Returns:
        str: Formatted score string
    """
    try:
        return f"{score:,}"
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting score: {e}")
        return "0"


def detect_terminal_features() -> Dict[str, bool]:
    """
    Detect terminal features and capabilities.
    
    Returns:
        Dict[str, bool]: Dictionary of terminal features
    """
    features = {
        'colors_256': False,
        'true_color': False,
        'unicode': False,
        'resizable': False
    }
    
    # Check for color support
    if 'COLORTERM' in os.environ:
        if os.environ['COLORTERM'] in ('truecolor', '24bit'):
            features['true_color'] = True
            features['colors_256'] = True
    
    if 'TERM' in os.environ:
        if '256' in os.environ['TERM']:
            features['colors_256'] = True
    
    # Check for Unicode support
    try:
        sys.stdout.write('▉')
        sys.stdout.flush()
        features['unicode'] = True
    except (UnicodeEncodeError, IOError):
        pass
    
    # Windows Terminal and many modern terminals are resizable
    features['resizable'] = True
    
    logger.info(f"Terminal features detected: {features}")
    return features


def backup_file(file_path: str) -> bool:
    """
    Create a backup of a file.
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        bool: True if backup was successful
    """
    if not os.path.exists(file_path):
        return False
        
    backup_path = f"{file_path}.bak"
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup of {file_path} to {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup of {file_path}: {e}")
        return False


def clean_exit(exit_code: int = 0):
    """
    Clean up before exiting the application.
    
    Args:
        exit_code: Exit code to return
    """
    try:
        # Reset terminal
        if WINDOWS:
            os.system('cls')
        else:
            os.system('clear')
            
        # Show cursor if hidden
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        
        logger.info(f"Clean exit with code {exit_code}")
    except Exception as e:
        logger.error(f"Error during clean exit: {e}")
    
    sys.exit(exit_code) 