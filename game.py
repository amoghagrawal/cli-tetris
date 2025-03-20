import random
import time

from constants import (
    INITIAL_SPEED, SPEED_INCREASE, LEVEL_SPEED_INCREASE, MIN_SPEED,
    POINTS_SINGLE, POINTS_DOUBLE, POINTS_TRIPLE, POINTS_TETRIS, LINES_PER_LEVEL,
    KEY_QUIT, KEY_PAUSE, KEY_RESTART, KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_DROP, KEY_ROTATE,
    START_X, START_Y, SHAPES, WALL_KICK_ATTEMPTS
)
from board import Board
from tetromino import Tetromino


class TetrisGame:
    def __init__(self, ui):
        """
        Initialize a new Tetris game
        
        Args:
            ui (GameUI): The game UI
        """
        self.ui = ui
        self.board = Board()
        self.current_tetromino = None
        self.next_tetromino = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.speed = INITIAL_SPEED
        self.last_drop_time = time.time()
        self.ghost_tetromino = None
        
        # Generate initial tetrominos
        self._generate_tetromino()
        self._generate_next_tetromino()
    
    def _generate_tetromino(self):
        """Generate a new tetromino at the top of the board"""
        if self.next_tetromino:
            self.current_tetromino = self.next_tetromino
        else:
            self.current_tetromino = Tetromino.random()
        
        # Check if the new tetromino collides - game over
        if not self.board.is_valid_position(self.current_tetromino):
            self.game_over = True
        
        # Update ghost piece
        self._update_ghost_position()
    
    def _generate_next_tetromino(self):
        """Generate the next tetromino to appear"""
        self.next_tetromino = Tetromino.random(x=0, y=0)
    
    def _update_ghost_position(self):
        """Update the ghost tetromino showing where the current piece will land"""
        if self.current_tetromino and not self.game_over:
            self.ghost_tetromino = self.current_tetromino.get_ghost_position(self.board)
    
    def move_left(self):
        """Move the current tetromino left"""
        if self.game_over or self.paused:
            return
        
        self.current_tetromino.move_left()
        if not self.board.is_valid_position(self.current_tetromino):
            # Revert if invalid
            self.current_tetromino.move_right()
        else:
            # Update ghost position
            self._update_ghost_position()
    
    def move_right(self):
        """Move the current tetromino right"""
        if self.game_over or self.paused:
            return
        
        self.current_tetromino.move_right()
        if not self.board.is_valid_position(self.current_tetromino):
            # Revert if invalid
            self.current_tetromino.move_left()
        else:
            # Update ghost position
            self._update_ghost_position()
    
    def move_down(self):
        """
        Move the current tetromino down
        
        Returns:
            bool: True if tetromino was locked in place, False otherwise
        """
        if self.game_over or self.paused:
            return False
        
        self.current_tetromino.move_down()
        if not self.board.is_valid_position(self.current_tetromino):
            # Revert if invalid and lock the tetromino
            self.current_tetromino.move(0, -1)
            self._lock_tetromino()
            return True
        
        return False
    
    def hard_drop(self):
        """Drop the tetromino instantly"""
        if self.game_over or self.paused:
            return
        
        # Use ghost position for instant drop
        if self.ghost_tetromino:
            self.current_tetromino.x = self.ghost_tetromino.x
            self.current_tetromino.y = self.ghost_tetromino.y
            self._lock_tetromino()
    
    def rotate(self):
        """Rotate the current tetromino"""
        if self.game_over or self.paused:
            return
        
        original_rotation = self.current_tetromino.rotation
        original_x = self.current_tetromino.x
        original_y = self.current_tetromino.y
        
        # Try to rotate
        self.current_tetromino.rotate_clockwise()
        if self.board.is_valid_position(self.current_tetromino):
            self._update_ghost_position()
            return
        
        # Try wall kicks if rotation failed
        # First try left, right, and up offsets
        offsets = [(-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]
        for dx, dy in offsets[:WALL_KICK_ATTEMPTS]:
            self.current_tetromino.x = original_x + dx
            self.current_tetromino.y = original_y + dy
            if self.board.is_valid_position(self.current_tetromino):
                self._update_ghost_position()
                return
        
        # If all fails, revert the rotation
        self.current_tetromino.x = original_x
        self.current_tetromino.y = original_y
        self.current_tetromino.rotation = original_rotation
    
    def toggle_pause(self):
        """Toggle the game paused state"""
        self.paused = not self.paused
    
    def _lock_tetromino(self):
        """Lock the current tetromino in place and generate a new one"""
        self.board.place_tetromino(self.current_tetromino)
        
        # Clear lines and update score
        lines_cleared = self.board.clear_lines()
        self._update_score(lines_cleared)
        
        # Generate new tetromino
        self._generate_tetromino()
        self._generate_next_tetromino()
    
    def _update_score(self, lines_cleared):
        """
        Update score based on lines cleared
        
        Args:
            lines_cleared (int): Number of lines cleared
        """
        self.lines_cleared += lines_cleared
        
        # Calculate score for this clear
        if lines_cleared == 1:
            points = POINTS_SINGLE
        elif lines_cleared == 2:
            points = POINTS_DOUBLE
        elif lines_cleared == 3:
            points = POINTS_TRIPLE
        elif lines_cleared == 4:
            points = POINTS_TETRIS
        else:
            points = 0
        
        # Apply level multiplier
        self.score += points * self.level
        
        # Check for level up
        if self.lines_cleared >= self.level * LINES_PER_LEVEL:
            self.level += 1
            self.speed -= LEVEL_SPEED_INCREASE
            self.speed = max(MIN_SPEED, self.speed)  # Ensure minimum speed
    
    def handle_input(self, key):
        """
        Handle a keypress
        
        Args:
            key: The key that was pressed
        """
        if key == KEY_QUIT:
            return False  # Signal to quit
        
        elif key == KEY_PAUSE:
            self.toggle_pause()
        
        elif not self.paused and not self.game_over:
            if key == KEY_LEFT:
                self.move_left()
            elif key == KEY_RIGHT:
                self.move_right()
            elif key == KEY_DOWN:
                self.move_down()
            elif key == KEY_DROP:
                self.hard_drop()
            elif key == KEY_ROTATE:
                self.rotate()
        
        # Allow restart if game over
        elif self.game_over and key == KEY_RESTART:
            self.__init__(self.ui)
        
        return True  # Continue game
    
    def update(self):
        """Update game state"""
        if self.paused or self.game_over:
            return
        
        current_time = time.time()
        elapsed = current_time - self.last_drop_time
        
        if elapsed >= self.speed:
            self.last_drop_time = current_time
            self.move_down()
            
            # Gradually increase speed
            self.speed = max(MIN_SPEED, self.speed - SPEED_INCREASE)
    
    def draw(self):
        """Draw the game"""
        self.ui.draw(
            self.board,
            self.current_tetromino,
            self.next_tetromino,
            self.ghost_tetromino,
            self.game_over,
            self.paused,
            self.score,
            self.level,
            self.lines_cleared
        ) 