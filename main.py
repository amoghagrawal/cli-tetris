#!/usr/bin/env python3
import sys
import asyncio
import argparse
import signal
import os
import logging
import platform
import traceback
from typing import Optional

from game import TetrisGame
from ui import TetrisUI
from constants import INITIAL_SPEED
from utils import get_terminal_size, set_terminal_size, is_terminal_size_sufficient, clean_exit
from config import load_config, save_config, get_difficulty_settings, DIFFICULTY_PRESETS, reset_config
import high_scores


# Setup logging
def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application"""
    level = logging.DEBUG if debug else logging.INFO
    
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(log_dir, "tetris_log.txt")
    
    try:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout) if debug else logging.NullHandler()
            ]
        )
    except (IOError, PermissionError) as e:
        # If log file can't be created, log to console only
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        logging.warning(f"Could not create log file at {log_file}: {e}")
    
    # Log platform information
    logger = logging.getLogger('tetris')
    logger.info(f"Starting Tetris on {platform.system()} {platform.release()} ({platform.version()})")
    logger.info(f"Python version: {platform.python_version()}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Terminal-based Tetris game")
    
    parser.add_argument(
        "--level", 
        type=int, 
        default=None,
        help="Starting level (1-10, default: 1)"
    )
    
    parser.add_argument(
        "--speed", 
        type=float, 
        default=None,
        help=f"Initial speed in seconds per drop (default: {INITIAL_SPEED})"
    )
    
    parser.add_argument(
        "--fullscreen", 
        action="store_true",
        help="Start in fullscreen mode"
    )
    
    parser.add_argument(
        "--size",
        type=str,
        help="Set terminal size as WIDTHxHEIGHT (e.g. 120x40)"
    )
    
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=list(DIFFICULTY_PRESETS.keys()),
        default=None,
        help="Game difficulty level"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom configuration file"
    )
    
    parser.add_argument(
        "--high-scores",
        action="store_true",
        help="Show high scores and exit"
    )
    
    parser.add_argument(
        "--reset-scores",
        action="store_true",
        help="Reset high scores"
    )
    
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset configuration to defaults"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging"
    )
    
    args = parser.parse_args()
    
    # Validate level if provided
    if args.level is not None and (args.level < 1 or args.level > 10):
        parser.error("Level must be between 1 and 10")
    
    return args


def show_high_scores():
    """Display high scores and exit"""
    logger = logging.getLogger('tetris')
    
    try:
        config = load_config()
        scores = high_scores.load_high_scores(config.get('high_scores_file', high_scores.DEFAULT_SCORES_FILE))
        
        if not scores:
            print("No high scores yet!")
            return
        
        print("\n===== HIGH SCORES =====\n")
        
        for line in high_scores.format_high_scores(scores):
            print(line)
    except Exception as e:
        logger.error(f"Error displaying high scores: {e}")
        print(f"Error: Could not display high scores: {e}")


def reset_high_scores():
    """Reset high scores"""
    logger = logging.getLogger('tetris')
    
    try:
        config = load_config()
        success = high_scores.reset_high_scores(config.get('high_scores_file', high_scores.DEFAULT_SCORES_FILE))
        
        if success:
            print("High scores reset successfully.")
        else:
            print("Failed to reset high scores.")
    except Exception as e:
        logger.error(f"Error resetting high scores: {e}")
        print(f"Error: Could not reset high scores: {e}")


async def shutdown(loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Handle graceful shutdown"""
    logger = logging.getLogger('tetris')
    logger.info("Shutting down...")
    
    print("\nShutting down...")
    
    # If no loop provided, get the current one
    if loop is None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
    
    # Cancel all tasks
    try:
        tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task()]
        
        if tasks:
            for task in tasks:
                task.cancel()
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        loop.stop()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    # Clean up terminal
    clean_exit()


async def main():
    """Main entry point for the Tetris game"""
    logger = logging.getLogger('tetris')
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging based on debug flag
    setup_logging(args.debug)
    
    # Handle special commands
    if args.high_scores:
        show_high_scores()
        return 0
    
    if args.reset_scores:
        reset_high_scores()
        return 0
    
    if args.reset_config:
        if reset_config():
            print("Configuration reset to defaults.")
        else:
            print("Failed to reset configuration.")
        return 0
    
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        logger.critical(f"Failed to load configuration: {e}")
        print(f"Error: Failed to load configuration: {e}")
        return 1
        
    # Set up signal handlers for graceful shutdown
    try:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop)))
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                if os.name == 'nt':
                    signal.signal(sig, lambda s, f: asyncio.create_task(shutdown(loop)))
    except (RuntimeError, AttributeError) as e:
        logger.warning(f"Could not set up signal handlers: {e}")
    
    # Update config from command line arguments
    if args.fullscreen:
        config['fullscreen'] = True
    
    if args.size:
        try:
            width, height = map(int, args.size.lower().split('x'))
            config['terminal_size'] = [width, height]
        except ValueError:
            logger.error("Invalid size format. Use WIDTHxHEIGHT (e.g. 120x40)")
            print("Error: Invalid size format. Use WIDTHxHEIGHT (e.g. 120x40)")
            return 1
    
    if args.difficulty:
        config['difficulty'] = args.difficulty
    
    # Save updated config
    try:
        save_config(config)
    except Exception as e:
        logger.warning(f"Could not save configuration: {e}")
    
    # Get difficulty settings
    difficulty_settings = get_difficulty_settings(config['difficulty'])
    
    try:
        # Check terminal size
        current_width, current_height = get_terminal_size()
        logger.info(f"Terminal size: {current_width}x{current_height}")
        
        # Set custom size if specified
        if 'terminal_size' in config:
            width, height = config['terminal_size']
            if set_terminal_size(width, height):
                logger.info(f"Terminal size set to {width}x{height}")
            else:
                logger.warning(f"Failed to set terminal size to {width}x{height}")
        
        # Set fullscreen if requested
        elif config.get('fullscreen', False):
            # Use larger size for fullscreen
            success = set_terminal_size(120, 40)
            if success:
                logger.info("Fullscreen mode enabled")
            else:
                logger.warning("Failed to set fullscreen mode")
        
        # Check if terminal is large enough
        if not is_terminal_size_sufficient(80, 24):
            logger.warning("Terminal size may be too small for optimal gameplay")
            print("Warning: Terminal size may be too small for optimal gameplay.")
            print("Consider using --fullscreen or --size options.")
            # Give user a chance to read the warning
            input("Press Enter to continue...")
            
        # Create the UI first
        ui = TetrisUI(None)  # Temporarily pass None
        
        # Create the game with the UI and custom settings
        game = TetrisGame(ui)
        
        # Apply settings
        game.level = args.level if args.level is not None else 1
        
        # Apply speed from args or difficulty settings
        if args.speed is not None:
            game.speed = args.speed / game.level  # Adjust for level
        else:
            game.speed = difficulty_settings['initial_speed'] / game.level
        
        # Apply other difficulty settings
        game.speed_increase = difficulty_settings['speed_increase']
        game.level_speed_increase = difficulty_settings['level_speed_increase']
        game.lines_per_level = difficulty_settings['lines_per_level']
        
        # Update the UI with the game reference
        ui.game = game
        
        # Print game info
        logger.info(f"Starting game with difficulty: {config['difficulty']}")
        logger.info(f"Level: {game.level}, Speed: {game.speed:.2f}")
        print(f"Starting game with difficulty: {config['difficulty']}")
        print(f"Level: {game.level}, Speed: {game.speed:.2f}")
        print("Press Q to quit, P to pause")
        
        # Start the UI (this will run the game)
        await ui.run()
        
    except KeyboardInterrupt:
        logger.info("Game terminated by keyboard interrupt")
        await shutdown()
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        logger.critical(traceback.format_exc())
        print(f"Error: {e}")
        await shutdown()
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nGame terminated by user")
        # Ensure terminal is reset
        clean_exit()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check the log file for details.")
        # Try to log the error
        try:
            logging.critical(f"Unhandled exception: {e}")
            logging.critical(traceback.format_exc())
        except:
            pass
        # Ensure terminal is reset
        clean_exit(1) 