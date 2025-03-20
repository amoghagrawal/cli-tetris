#!/usr/bin/env python3
import sys
import time
import os
import keyboard  # Cross-platform keyboard input

from game import TetrisGame
from ui import GameUI
from constants import KEY_QUIT, KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_ROTATE, KEY_DROP, KEY_PAUSE, KEY_RESTART


def get_key():
    """Get a keypress without blocking"""
    # Check for arrow keys
    if keyboard.is_pressed('up'):
        return KEY_ROTATE
    elif keyboard.is_pressed('down'):
        return KEY_DOWN
    elif keyboard.is_pressed('left'):
        return KEY_LEFT
    elif keyboard.is_pressed('right'):
        return KEY_RIGHT
    # Check for other keys
    elif keyboard.is_pressed('space'):
        return KEY_DROP
    elif keyboard.is_pressed('p'):
        return KEY_PAUSE
    elif keyboard.is_pressed('q'):
        return KEY_QUIT
    elif keyboard.is_pressed('r'):
        return KEY_RESTART
            
    return None


def main():
    """Main entry point for the Tetris game"""
    # Initialize UI and game
    try:
        ui = GameUI()
        game = TetrisGame(ui)
        
        # Main game loop
        running = True
        last_key_time = time.time()
        
        while running:
            # Handle input (with debouncing)
            current_time = time.time()
            if current_time - last_key_time > 0.1:  # 100ms debounce
                key_pressed = get_key()
                if key_pressed is not None:
                    running = game.handle_input(key_pressed)
                    last_key_time = current_time
            
            # Update game state
            game.update()
            
            # Draw game
            game.draw()
            
            # Sleep to limit CPU usage
            time.sleep(0.05)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    sys.exit(0)


if __name__ == "__main__":
    main() 