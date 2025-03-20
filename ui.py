from batgrl.app import App
from batgrl.colors import rgb_to_hex, hex_to_rgb
from batgrl.gadgets.pane import Pane
from batgrl.gadgets.text import Text
import asyncio
import logging
import traceback
import signal
import time
import os
import sys

from constants import (
    BOARD_WIDTH, BOARD_HEIGHT,
    PREVIEW_WIDTH, PREVIEW_HEIGHT
)
from utils import translate_key, safe_color_blend, format_score, format_time
import high_scores
from config import load_config, get_key_map, save_config


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='tetris_log.txt',
    filemode='a'
)
logger = logging.getLogger('tetris')

# Define colors for the blocks (similar to the image)
TETRIS_COLORS = {
    'I': '#00FFFF',  # Cyan
    'J': '#0000FF',  # Blue
    'L': '#FF7F00',  # Orange
    'O': '#FFFF00',  # Yellow
    'S': '#00FF00',  # Green
    'T': '#800080',  # Purple
    'Z': '#FF0000',  # Red
    'EMPTY': '#000033',  # Darker blue for board background
    'BORDER': '#9370DB',  # Medium purple
    'GHOST': '#333333',  # Dark gray
    'BACKGROUND': '#000022',  # Very dark blue background
    'TEXT': '#FFFFFF',  # White
    'PANEL': '#241144',  # Darker purple for panels (to match image)
}


class TetrisUI(App):
    def __init__(self, game):
        try:
            self.game = game
            self.block_size = 2  # Make blocks larger to match the reference image
            self.grid_offset_x = 0
            self.grid_offset_y = 0
            self.board_shapes = {}
            self.next_piece_shapes = {}
            self.hold_piece_shapes = {}
            self.ghost_pieces = {}
            self.active_piece_shapes = {}
            self.score_text = None
            self.level_text = None
            self.lines_text = None
            self.game_over_overlay = None
            self.pause_overlay = None
            self.start_time = None
            self.game_time_text = None
            self.high_score_overlay = None
            
            # Load configuration with error handling
            try:
                self.config = load_config()
                self.key_map = get_key_map(self.config)
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                # Fallback to defaults
                from config import DEFAULT_CONTROLS
                self.config = {'controls': DEFAULT_CONTROLS}
                self.key_map = get_key_map(self.config)
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            super().__init__()
        except Exception as e:
            logger.critical(f"Error initializing UI: {str(e)}")
            logger.critical(traceback.format_exc())
            print(f"Critical error initializing UI: {str(e)}")
            sys.exit(1)

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        try:
            # Only set signal handlers if in main thread
            if asyncio.get_event_loop().is_running():
                for sig in (signal.SIGINT, signal.SIGTERM):
                    try:
                        asyncio.get_event_loop().add_signal_handler(
                            sig, 
                            lambda: asyncio.create_task(self._cleanup_and_exit())
                        )
                    except NotImplementedError:
                        # Windows doesn't support add_signal_handler
                        if os.name == 'nt':
                            signal.signal(sig, lambda s, f: asyncio.create_task(self._cleanup_and_exit()))
        except (RuntimeError, AttributeError):
            # Not in event loop or other issue
            pass

    async def _cleanup_and_exit(self):
        """Perform cleanup before exiting"""
        try:
            # Save current score if it's a high score
            if self.game and not self.game.game_over and self.game.score > 0:
                elapsed = 0
                if self.start_time:
                    elapsed = time.time() - self.start_time
                
                if high_scores.is_high_score(self.game.score):
                    high_scores.add_high_score(
                        self.game.score, 
                        self.game.level, 
                        self.game.lines_cleared, 
                        elapsed,
                        self.config.get('high_scores_file', high_scores.DEFAULT_SCORES_FILE)
                    )
                    logger.info(f"Saved high score on exit: {self.game.score}")
            
            # Save any config changes
            save_config(self.config)
            logger.info("Configuration saved on exit")
            
            # Exit the app
            self.exit()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def on_start(self):
        try:
            # Record start time
            import time
            self.start_time = time.time()
            
            # Background
            self.background = Pane(
                size=(self.height, self.width),
                bg_color=TETRIS_COLORS['BACKGROUND'],
                pos=(0, 0)
            )
            self.add_gadget(self.background)
            
            # Calculate positions
            board_pixel_width = BOARD_WIDTH * self.block_size
            board_pixel_height = BOARD_HEIGHT * self.block_size
            
            # Center the board on screen
            self.grid_offset_x = (self.width - board_pixel_width) // 2
            self.grid_offset_y = (self.height - board_pixel_height) // 2
            
            # Create main game field
            self.game_field = Pane(
                size=(board_pixel_height, board_pixel_width),
                pos=(self.grid_offset_y, self.grid_offset_x),
                bg_color=TETRIS_COLORS['EMPTY']
            )
            self.background.add_gadget(self.game_field)
            
            # Create decorative background pattern (stair-steps on the sides)
            self.create_decorative_background()
            
            # Create left panel (HOLD)
            self.left_panel = Pane(
                size=(12, 10),  # Taller panel
                pos=(self.grid_offset_y, self.grid_offset_x - 12),
                bg_color=TETRIS_COLORS['PANEL']
            )
            self.hold_label = Text(
                text="HOLD",
                pos=(2, 3),  # Center text
                color=TETRIS_COLORS['TEXT']
            )
            self.left_panel.add_gadget(self.hold_label)
            self.background.add_gadget(self.left_panel)
            
            # Create right panel (NEXT)
            self.right_panel = Pane(
                size=(12, 10),  # Taller panel
                pos=(self.grid_offset_y, self.grid_offset_x + board_pixel_width + 2),
                bg_color=TETRIS_COLORS['PANEL']
            )
            self.next_label = Text(
                text="NEXT",
                pos=(2, 3),  # Center text
                color=TETRIS_COLORS['TEXT']
            )
            self.right_panel.add_gadget(self.next_label)
            self.background.add_gadget(self.right_panel)
            
            # Create score panel (moved to bottom part of left side like in the image)
            self.score_panel = Pane(
                size=(8, 10),
                pos=(self.grid_offset_y + board_pixel_height - 20, self.grid_offset_x - 12),
                bg_color=TETRIS_COLORS['PANEL']
            )
            self.score_label = Text(
                text="SCORE",
                pos=(2, 2),
                color=TETRIS_COLORS['TEXT']
            )
            self.score_text = Text(
                text="0",
                pos=(4, 2),
                color=TETRIS_COLORS['TEXT']
            )
            self.score_panel.add_gadgets(self.score_label, self.score_text)
            self.background.add_gadget(self.score_panel)
            
            # Create level panel (moved to bottom part of right side like in the image)
            self.level_panel = Pane(
                size=(8, 10),
                pos=(self.grid_offset_y + board_pixel_height - 20, self.grid_offset_x + board_pixel_width + 2),
                bg_color=TETRIS_COLORS['PANEL']
            )
            self.level_label = Text(
                text="LEVEL",
                pos=(2, 2),
                color=TETRIS_COLORS['TEXT']
            )
            self.level_text = Text(
                text="1",
                pos=(4, 2),
                color=TETRIS_COLORS['TEXT']
            )
            self.lines_label = Text(
                text="Lines:",
                pos=(6, 2),
                color=TETRIS_COLORS['TEXT']
            )
            self.lines_text = Text(
                text="0",
                pos=(7, 3),
                color=TETRIS_COLORS['TEXT']
            )
            self.level_panel.add_gadgets(self.level_label, self.level_text, self.lines_label, self.lines_text)
            self.background.add_gadget(self.level_panel)
            
            # Create pause overlay (hidden by default)
            self.pause_overlay = Pane(
                size=(10, 20),
                pos=(self.grid_offset_y + board_pixel_height // 2 - 5, self.grid_offset_x + board_pixel_width // 2 - 10),
                bg_color=TETRIS_COLORS['PANEL'],
                visible=False
            )
            self.pause_text = Text(
                text="PAUSED",
                pos=(3, 6),
                color=TETRIS_COLORS['TEXT']
            )
            self.pause_help = Text(
                text="Press P to resume\nPress Q to quit",
                pos=(5, 3),
                color=TETRIS_COLORS['TEXT']
            )
            self.pause_overlay.add_gadgets(self.pause_text, self.pause_help)
            self.background.add_gadget(self.pause_overlay)
            
            # Create game over overlay (hidden by default)
            self.game_over_overlay = Pane(
                size=(10, 20),
                pos=(self.grid_offset_y + board_pixel_height // 2 - 5, self.grid_offset_x + board_pixel_width // 2 - 10),
                bg_color=TETRIS_COLORS['PANEL'],
                visible=False
            )
            self.game_over_text = Text(
                text="GAME OVER",
                pos=(3, 5),
                color=TETRIS_COLORS['TEXT']
            )
            self.game_over_help = Text(
                text="Press R to restart\nPress Q to quit",
                pos=(5, 3),
                color=TETRIS_COLORS['TEXT']
            )
            self.game_over_overlay.add_gadgets(self.game_over_text, self.game_over_help)
            self.background.add_gadget(self.game_over_overlay)
            
            # Create high score overlay (hidden by default)
            self.high_score_overlay = Pane(
                size=(15, 30),
                pos=(self.grid_offset_y + board_pixel_height // 2 - 8, self.grid_offset_x + board_pixel_width // 2 - 15),
                bg_color=TETRIS_COLORS['PANEL'],
                visible=False
            )
            self.high_score_title = Text(
                text="HIGH SCORES",
                pos=(2, 10),
                color=TETRIS_COLORS['TEXT']
            )
            self.high_score_list = Text(
                text="",
                pos=(4, 2),
                color=TETRIS_COLORS['TEXT']
            )
            self.high_score_help = Text(
                text="Press any key to continue",
                pos=(13, 5),
                color=TETRIS_COLORS['TEXT']
            )
            self.high_score_overlay.add_gadgets(self.high_score_title, self.high_score_list, self.high_score_help)
            self.background.add_gadget(self.high_score_overlay)

        except Exception as e:
            logger.error(f"Error in on_start: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"Error starting UI: {str(e)}")
            self.exit()

    def create_decorative_background(self):
        """Create decorative background pattern seen in the reference image"""
        # Left side stairs
        for i in range(5):
            step = Pane(
                size=(4, 15 - i*2),
                pos=(self.grid_offset_y + 20 + i*4, self.grid_offset_x - 15 + i*2),
                bg_color=rgb_to_hex(100, 50, 150)  # Light purple
            )
            self.background.add_gadget(step)
        
        # Right side stairs
        for i in range(5):
            step = Pane(
                size=(4, 15 - i*2),
                pos=(self.grid_offset_y + 20 + i*4, self.grid_offset_x + BOARD_WIDTH * self.block_size + i*2),
                bg_color=rgb_to_hex(100, 50, 150)  # Light purple
            )
            self.background.add_gadget(step)

    def on_key(self, key_event):
        """Handle key events"""
        try:
            # Translate key for alternative layouts
            key = translate_key(key_event.key, self.key_map)
            
            # Pass key to game
            if key == "q":
                asyncio.create_task(self._cleanup_and_exit())
                return True
            else:
                return self.game.handle_input(key)
        except Exception as e:
            logger.error(f"Error processing key event: {str(e)}")
            return False

    def update_display(self):
        """Update the display based on the current game state"""
        try:
            import time
            
            # Check if game just ended and we need to show high scores
            if self.game.game_over and not self.high_score_overlay.visible and not self.game_over_overlay.visible:
                # Check if this is a high score
                elapsed = 0
                if self.start_time:
                    elapsed = time.time() - self.start_time
                
                if high_scores.is_high_score(self.game.score):
                    # Add the score
                    try:
                        high_scores.add_high_score(
                            self.game.score, 
                            self.game.level, 
                            self.game.lines_cleared, 
                            elapsed,
                            self.config.get('high_scores_file', high_scores.DEFAULT_SCORES_FILE)
                        )
                        
                        # Show high scores
                        self._show_high_scores()
                    except Exception as e:
                        logger.error(f"Failed to save high score: {e}")
                        # Show game over if we can't save score
                        self.game_over_overlay.visible = True
                else:
                    # Show game over
                    self.game_over_overlay.visible = True
            
            # Update score, level and lines
            self.score_text.text = format_score(self.game.score).rjust(6)  # Right-align with fixed width
            self.level_text.text = str(self.game.level).center(3)  # Center align
            self.lines_text.text = str(self.game.lines_cleared)
            
            # Update game time
            if self.start_time:
                elapsed = time.time() - self.start_time
                if not self.game.paused:
                    self.game_time_text.text = format_time(elapsed) if hasattr(self, 'game_time_text') else ""
            
            # Clear previous pieces
            for shape in self.board_shapes.values():
                shape.kill()
            self.board_shapes.clear()
            
            for shape in self.active_piece_shapes.values():
                shape.kill()
            self.active_piece_shapes.clear()
            
            for shape in self.ghost_pieces.values():
                shape.kill()
            self.ghost_pieces.clear()
            
            for shape in self.next_piece_shapes.values():
                shape.kill()
            self.next_piece_shapes.clear()
            
            for shape in self.hold_piece_shapes.values():
                shape.kill()
            self.hold_piece_shapes.clear()
            
            # Draw board
            for y in range(self.game.board.height):
                for x in range(self.game.board.width):
                    cell = self.game.board.grid[y][x]
                    if cell is not None:
                        pos_x = self.grid_offset_x + x * self.block_size
                        pos_y = self.grid_offset_y + y * self.block_size
                        block = Pane(
                            size=(self.block_size, self.block_size),
                            pos=(pos_y, pos_x),
                            bg_color=TETRIS_COLORS[cell],
                            filled=True,  # Ensure filled
                            line_width=0  # No border for cleaner look
                        )
                        self.game_field.add_gadget(block)
                        self.board_shapes[(x, y)] = block
            
            # Draw active piece
            if self.game.current_tetromino:
                for x, y in self.game.current_tetromino.get_coords():
                    if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                        pos_x = self.grid_offset_x + x * self.block_size
                        pos_y = self.grid_offset_y + y * self.block_size
                        block = Pane(
                            size=(self.block_size, self.block_size),
                            pos=(pos_y, pos_x),
                            bg_color=TETRIS_COLORS[self.game.current_tetromino.shape_type],
                            filled=True,  # Ensure filled
                            line_width=0  # No border for cleaner look
                        )
                        self.game_field.add_gadget(block)
                        self.active_piece_shapes[(x, y)] = block
            
            # Draw ghost piece
            if self.game.ghost_tetromino and not self.game.game_over:
                for x, y in self.game.ghost_tetromino.get_coords():
                    if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                        # Only draw ghost if no active piece at this location
                        if (x, y) not in self.active_piece_shapes:
                            pos_x = self.grid_offset_x + x * self.block_size
                            pos_y = self.grid_offset_y + y * self.block_size
                            
                            # Create a ghost block using color blending
                            color = TETRIS_COLORS[self.game.current_tetromino.shape_type]
                            ghost_color = safe_color_blend(color, TETRIS_COLORS['EMPTY'], 0.7)
                            
                            block = Pane(
                                size=(self.block_size, self.block_size),
                                pos=(pos_y, pos_x),
                                bg_color=ghost_color,
                                filled=False,
                                line_width=0.1
                            )
                            self.game_field.add_gadget(block)
                            self.ghost_pieces[(x, y)] = block
            
            # Draw next piece
            if self.game.next_tetromino:
                # Center in the preview panel
                offset_x = 3
                offset_y = 4  # Adjusted for better centering
                for dx, dy in self.game.next_tetromino.get_coords():
                    pos_x = offset_x + dx
                    pos_y = offset_y + dy
                    block = Pane(
                        size=(2, 2),  # Larger blocks for preview
                        pos=(pos_y, pos_x),
                        bg_color=TETRIS_COLORS[self.game.next_tetromino.shape_type],
                        filled=True,  # Ensure filled
                        line_width=0  # No border for cleaner look
                    )
                    self.right_panel.add_gadget(block)
                    self.next_piece_shapes[(dx, dy)] = block
                    
            # Draw hold piece
            if self.game.hold_tetromino:
                # Center in the hold panel
                offset_x = 3
                offset_y = 4  # Adjusted for better centering
                for dx, dy in self.game.hold_tetromino.get_coords():
                    pos_x = offset_x + dx
                    pos_y = offset_y + dy
                    # Use lighter color if can't hold
                    color = TETRIS_COLORS[self.game.hold_tetromino.shape_type]
                    if not self.game.can_hold:
                        color = safe_color_blend(color, TETRIS_COLORS['EMPTY'], 0.5)
                        
                    block = Pane(
                        size=(2, 2),  # Larger blocks for hold
                        pos=(pos_y, pos_x),
                        bg_color=color,
                        filled=True,  # Ensure filled
                        line_width=0  # No border for cleaner look
                    )
                    self.left_panel.add_gadget(block)
                    self.hold_piece_shapes[(dx, dy)] = block
            
            # Show/hide overlays based on game state
            self.pause_overlay.visible = self.game.paused
            self.game_over_overlay.visible = self.game.game_over

        except Exception as e:
            logger.error(f"Error updating display: {str(e)}")
            logger.error(traceback.format_exc())

    def _show_high_scores(self):
        """Show the high scores overlay"""
        try:
            # Load high scores
            scores = high_scores.load_high_scores(
                self.config.get('high_scores_file', high_scores.DEFAULT_SCORES_FILE)
            )
            
            # Format for display
            formatted_scores = high_scores.format_high_scores(scores)
            
            # Build the score text
            score_text = "\n".join(formatted_scores[:7])  # Show only top 7 scores to fit
            self.high_score_list.text = score_text
            
            # Hide game over overlay, show high scores
            self.game_over_overlay.visible = False
            self.high_score_overlay.visible = True
        except Exception as e:
            logger.error(f"Error showing high scores: {str(e)}")
            # Fallback to game over screen
            self.game_over_overlay.visible = True

    async def run(self):
        """Start the UI and run the game loop"""
        try:
            # Start the UI
            with self:
                # Wait for the UI to be ready
                await self.start()
                # Start the game loop
                await self.game.game_loop()
        except Exception as e:
            logger.critical(f"Critical error in UI run: {str(e)}")
            logger.critical(traceback.format_exc())
            print(f"Game crashed: {str(e)}")
            # Try to cleanup
            await self._cleanup_and_exit() 