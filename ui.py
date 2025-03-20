from batgrl.io.term import Terminal
from batgrl.shapes.labels import Label
from batgrl.shapes.boxes import Box
from batgrl.shapes.lines import Line

from constants import (
    COLORS, BOARD_WIDTH, BOARD_HEIGHT, BLOCK_SIZE,
    PREVIEW_WIDTH, PREVIEW_HEIGHT, INFO_PADDING
)

from utils import format_score


class GameUI:
    def __init__(self, terminal):
        """
        Initialize the game UI
        
        Args:
            terminal (Terminal): The batgrl terminal instance
        """
        self.terminal = terminal
        self.width = terminal.width
        self.height = terminal.height
        
        # Calculate sizes and positions
        self.board_pixel_width = BOARD_WIDTH * BLOCK_SIZE
        self.board_pixel_height = BOARD_HEIGHT * BLOCK_SIZE
        
        # Center the board on screen
        self.board_x = (self.width - self.board_pixel_width) // 2
        self.board_y = (self.height - self.board_pixel_height) // 2
        
        # Create UI elements
        self.create_ui_elements()
        
    def create_ui_elements(self):
        """Create all the UI elements"""
        # Background
        self.background = Box(
            x=0,
            y=0,
            width=self.width,
            height=self.height,
            color=COLORS['BACKGROUND'],
            filled=True
        )
        
        # Game border
        self.game_border = Box(
            x=self.board_x - 1,
            y=self.board_y - 1,
            width=self.board_pixel_width + 2,
            height=self.board_pixel_height + 2,
            color=COLORS['BORDER']
        )
        
        # Title display
        self.title_label = Label(
            x=self.board_x + (self.board_pixel_width // 2) - 7,
            y=self.board_y - 5,
            text="TERMINAL TETRIS",
            color=COLORS['TEXT']
        )
        
        # Score display
        self.score_label = Label(
            x=self.board_x,
            y=self.board_y - 3,
            text="Score: 0",
            color=COLORS['TEXT']
        )
        
        # Level display
        self.level_label = Label(
            x=self.board_x + self.board_pixel_width - 8,
            y=self.board_y - 3,
            text="Level: 1",
            color=COLORS['TEXT']
        )
        
        # Lines display
        self.lines_label = Label(
            x=self.board_x,
            y=self.board_y - 2,
            text="Lines: 0",
            color=COLORS['TEXT']
        )
        
        # Next piece preview
        self.next_piece_label = Label(
            x=self.board_x + self.board_pixel_width + INFO_PADDING,
            y=self.board_y,
            text="Next:",
            color=COLORS['TEXT']
        )
        
        self.next_piece_box = Box(
            x=self.board_x + self.board_pixel_width + INFO_PADDING,
            y=self.board_y + 2,
            width=PREVIEW_WIDTH,
            height=PREVIEW_HEIGHT,
            color=COLORS['BORDER']
        )
        
        # Controls help
        self.controls_label = Label(
            x=self.board_x,
            y=self.board_y + self.board_pixel_height + INFO_PADDING,
            text="Controls: ←→↓ to move, ↑ to rotate, SPACE to drop, P to pause, Q to quit",
            color=COLORS['TEXT']
        )
        
        # Create grid lines for the board (optional, for visual appeal)
        self.grid_lines = []
        
        # Vertical grid lines
        for x in range(BOARD_WIDTH + 1):
            line = Line(
                x1=self.board_x + (x * BLOCK_SIZE),
                y1=self.board_y,
                x2=self.board_x + (x * BLOCK_SIZE),
                y2=self.board_y + self.board_pixel_height,
                color=COLORS['BORDER'],
                line_width=0.2
            )
            self.grid_lines.append(line)
            
        # Horizontal grid lines
        for y in range(BOARD_HEIGHT + 1):
            line = Line(
                x1=self.board_x,
                y1=self.board_y + (y * BLOCK_SIZE),
                x2=self.board_x + self.board_pixel_width,
                y2=self.board_y + (y * BLOCK_SIZE),
                color=COLORS['BORDER'],
                line_width=0.2
            )
            self.grid_lines.append(line)
    
    def draw_board(self, board):
        """
        Draw the game board
        
        Args:
            board (Board): The game board to draw
        """
        for y in range(board.height):
            for x in range(board.width):
                color = board.get_cell_color(x, y)
                
                # Draw block
                filled = board.grid[y][x] is not None
                self.draw_block(x, y, color, filled)
    
    def draw_tetromino(self, tetromino, is_ghost=False):
        """
        Draw a tetromino on the board
        
        Args:
            tetromino (Tetromino): The tetromino to draw
            is_ghost (bool): Whether this is a ghost tetromino
        """
        if not tetromino:
            return
            
        color = COLORS['GHOST'] if is_ghost else tetromino.color
        
        for x, y in tetromino.get_coords():
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                self.draw_block(x, y, color, True, is_ghost)
    
    def draw_block(self, board_x, board_y, color, filled=True, is_ghost=False):
        """
        Draw a single block at the given board coordinates
        
        Args:
            board_x (int): X coordinate on the board grid
            board_y (int): Y coordinate on the board grid
            color (str): Color hex code
            filled (bool): Whether the block is filled or empty
            is_ghost (bool): Whether this is a ghost block
        """
        pixel_x = self.board_x + (board_x * BLOCK_SIZE)
        pixel_y = self.board_y + (board_y * BLOCK_SIZE)
        
        if filled:
            block = Box(
                x=pixel_x,
                y=pixel_y,
                width=BLOCK_SIZE,
                height=BLOCK_SIZE,
                color=color,
                filled=not is_ghost,  # Ghost blocks are outlines
                line_width=1 if is_ghost else 0
            )
            self.terminal.add_shape(block)
    
    def update_score(self, score):
        """Update the score display"""
        self.score_label.text = f"Score: {format_score(score)}"
    
    def update_level(self, level):
        """Update the level display"""
        self.level_label.text = f"Level: {level}"
        
    def update_lines(self, lines):
        """Update the lines display"""
        self.lines_label.text = f"Lines: {lines}"
    
    def draw_next_piece(self, next_tetromino):
        """Draw the next tetromino in the preview box"""
        # Clear the preview box first
        self.terminal.add_shape(self.next_piece_box)
        
        if next_tetromino:
            # Center the piece in the preview box
            center_x = (PREVIEW_WIDTH - next_tetromino.width) // 2
            center_y = (PREVIEW_HEIGHT - next_tetromino.height) // 2
            
            for dx, dy in next_tetromino.get_coords():
                # Adjust coordinates for the preview box
                x = self.next_piece_box.x + center_x + dx + 1
                y = self.next_piece_box.y + center_y + dy + 1
                
                block = Box(
                    x=x,
                    y=y,
                    width=1,
                    height=1,
                    color=next_tetromino.color,
                    filled=True
                )
                self.terminal.add_shape(block)
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Semi-transparent overlay
        overlay = Box(
            x=self.board_x - 1,
            y=self.board_y - 1,
            width=self.board_pixel_width + 2,
            height=self.board_pixel_height + 2,
            color=COLORS['BACKGROUND'],
            filled=True,
            line_width=0,
            alpha=0.7
        )
        
        game_over_box = Box(
            x=self.board_x + 2,
            y=self.board_y + (self.board_pixel_height // 2) - 3,
            width=self.board_pixel_width - 4,
            height=6,
            color=COLORS['BORDER']
        )
        
        game_over_label = Label(
            x=self.board_x + (self.board_pixel_width // 2) - 4,
            y=self.board_y + (self.board_pixel_height // 2) - 1,
            text="GAME OVER",
            color=COLORS['I']  # Use a bright color
        )
        
        restart_label = Label(
            x=self.board_x + (self.board_pixel_width // 2) - 10,
            y=self.board_y + (self.board_pixel_height // 2) + 1,
            text="Press R to restart or Q to quit",
            color=COLORS['TEXT']
        )
        
        self.terminal.add_shape(overlay)
        self.terminal.add_shape(game_over_box)
        self.terminal.add_shape(game_over_label)
        self.terminal.add_shape(restart_label)
    
    def draw_pause_screen(self):
        """Draw the pause screen"""
        # Semi-transparent overlay
        overlay = Box(
            x=self.board_x - 1,
            y=self.board_y - 1,
            width=self.board_pixel_width + 2,
            height=self.board_pixel_height + 2,
            color=COLORS['BACKGROUND'],
            filled=True,
            line_width=0,
            alpha=0.7
        )
        
        pause_box = Box(
            x=self.board_x + 2,
            y=self.board_y + (self.board_pixel_height // 2) - 3,
            width=self.board_pixel_width - 4,
            height=6,
            color=COLORS['BORDER']
        )
        
        pause_label = Label(
            x=self.board_x + (self.board_pixel_width // 2) - 3,
            y=self.board_y + (self.board_pixel_height // 2) - 1,
            text="PAUSED",
            color=COLORS['O']  # Use a bright color
        )
        
        resume_label = Label(
            x=self.board_x + (self.board_pixel_width // 2) - 9,
            y=self.board_y + (self.board_pixel_height // 2) + 1,
            text="Press P to resume or Q to quit",
            color=COLORS['TEXT']
        )
        
        self.terminal.add_shape(overlay)
        self.terminal.add_shape(pause_box)
        self.terminal.add_shape(pause_label)
        self.terminal.add_shape(resume_label)
    
    def draw(self, board, current_tetromino=None, next_tetromino=None, ghost_tetromino=None, game_over=False, paused=False, lines_cleared=0):
        """
        Draw the complete game UI
        
        Args:
            board (Board): The game board
            current_tetromino (Tetromino): The currently falling tetromino
            next_tetromino (Tetromino): The next tetromino to appear
            ghost_tetromino (Tetromino): The ghost tetromino showing landing position
            game_over (bool): Whether the game is over
            paused (bool): Whether the game is paused
            lines_cleared (int): Total number of lines cleared
        """
        self.terminal.clear()
        
        # Draw background first
        self.terminal.add_shape(self.background)
        
        # Draw UI elements
        self.terminal.add_shape(self.title_label)
        self.terminal.add_shape(self.game_border)
        self.terminal.add_shape(self.score_label)
        self.terminal.add_shape(self.level_label)
        self.terminal.add_shape(self.lines_label)
        self.terminal.add_shape(self.next_piece_label)
        self.terminal.add_shape(self.controls_label)
        
        # Update lines count
        self.update_lines(lines_cleared)
        
        # Draw grid lines (optional)
        for line in self.grid_lines:
            self.terminal.add_shape(line)
        
        # Draw board and pieces
        self.draw_board(board)
        
        # Draw ghost piece first so active piece appears on top
        if ghost_tetromino and not game_over and not paused:
            self.draw_tetromino(ghost_tetromino, is_ghost=True)
            
        if current_tetromino:
            self.draw_tetromino(current_tetromino)
            
        if next_tetromino:
            self.draw_next_piece(next_tetromino)
        
        # Draw overlay screens if necessary
        if game_over:
            self.draw_game_over()
        elif paused:
            self.draw_pause_screen()
        
        self.terminal.print() 