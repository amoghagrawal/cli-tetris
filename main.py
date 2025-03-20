#!/usr/bin/env python3
import sys
import time
from batgrl.io.term import Terminal
from batgrl.io.keys import Keys

from game import TetrisGame
from ui import GameUI
from constants import KEY_QUIT


def main():
    """Main entry point for the Tetris game"""
    # Initialize terminal
    terminal = Terminal()
    terminal.hide_cursor()
    
    try:
        # Initialize UI and game
        ui = GameUI(terminal)
        game = TetrisGame(ui)
        
        # Main game loop
        running = True
        
        while running:
            # Handle input
            key_pressed = terminal.get_key_press()
            if key_pressed is not None:
                running = game.handle_input(key_pressed)
            
            # Update game state
            game.update()
            
            # Draw game
            game.draw()
            
            # Sleep to limit CPU usage
            time.sleep(0.05)
    except Exception as e:
        # Ensure we clean up terminal even if an error occurs
        terminal.cleanup()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # Clean up
        terminal.cleanup()
        
    sys.exit(0)


if __name__ == "__main__":
    main() 