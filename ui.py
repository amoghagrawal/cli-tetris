import os
import sys

from constants import (
    COLORS, BOARD_WIDTH, BOARD_HEIGHT, 
    PREVIEW_WIDTH, PREVIEW_HEIGHT
)

from utils import format_score


class GameUI:
    def __init__(self):
        """Initialize the console UI"""
        self.clear_screen()
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def draw_block(self, filled=False):
        """Draw a single block"""
        return "██" if filled else "  "
        
    def draw_ghost_block(self):
        """Draw a ghost block (outline)"""
        return "░░"
        
    def draw_board(self, board):
        """
        Draw the game board
        
        Args:
            board (Board): The game board to draw
        """
        board_str = "┌" + "──" * BOARD_WIDTH + "┐\n"
        
        for y in range(board.height):
            board_str += "│"
            for x in range(board.width):
                if board.grid[y][x] is not None:
                    board_str += self.draw_block(True)
                else:
                    board_str += self.draw_block(False)
            board_str += "│\n"
            
        board_str += "└" + "──" * BOARD_WIDTH + "┘"
        return board_str
        
    def draw_tetromino(self, board, tetromino, is_ghost=False):
        """
        Draw the tetromino on the board representation
        
        Args:
            board: 2D array representation of the board
            tetromino: The tetromino to draw
            is_ghost: Whether this is a ghost tetromino
        """
        if not tetromino:
            return board
            
        board_copy = [row[:] for row in board]
        
        for x, y in tetromino.get_coords():
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                board_copy[y][x] = "G" if is_ghost else tetromino.shape_type
                
        return board_copy
        
    def draw_next_piece(self, tetromino):
        """
        Draw the next tetromino preview
        
        Args:
            tetromino: The next tetromino
        """
        if not tetromino:
            return ""
            
        # Create empty grid
        grid = [[" " for _ in range(PREVIEW_WIDTH)] for _ in range(PREVIEW_HEIGHT)]
        
        # Center the piece
        center_x = (PREVIEW_WIDTH - tetromino.width) // 2
        center_y = (PREVIEW_HEIGHT - tetromino.height) // 2
        
        # Place the tetromino in the grid
        for dx, dy in tetromino.get_coords():
            x = center_x + dx
            y = center_y + dy
            if 0 <= y < PREVIEW_HEIGHT and 0 <= x < PREVIEW_WIDTH:
                grid[y][x] = tetromino.shape_type
                
        # Convert grid to string
        preview_str = "┌" + "──" * PREVIEW_WIDTH + "┐\n"
        for row in grid:
            preview_str += "│"
            for cell in row:
                if cell == " ":
                    preview_str += self.draw_block(False)
                else:
                    preview_str += self.draw_block(True)
            preview_str += "│\n"
        preview_str += "└" + "──" * PREVIEW_WIDTH + "┘"
        
        return preview_str
        
    def draw_game_over(self):
        """Draw the game over message"""
        return (
            "┌───────────────────┐\n"
            "│     GAME OVER     │\n"
            "│                   │\n"
            "│ Press R to restart│\n"
            "│  Press Q to quit  │\n"
            "└───────────────────┘"
        )
        
    def draw_pause_screen(self):
        """Draw the pause screen message"""
        return (
            "┌───────────────────┐\n"
            "│       PAUSED      │\n"
            "│                   │\n"
            "│ Press P to resume │\n"
            "│  Press Q to quit  │\n"
            "└───────────────────┘"
        )
    
    def draw(self, board, current_tetromino=None, next_tetromino=None, 
             ghost_tetromino=None, game_over=False, paused=False, 
             score=0, level=1, lines_cleared=0):
        """
        Draw the complete game UI
        
        Args:
            board (Board): The game board
            current_tetromino (Tetromino): The currently falling tetromino
            next_tetromino (Tetromino): The next tetromino to appear
            ghost_tetromino (Tetromino): The ghost tetromino showing landing position
            game_over (bool): Whether the game is over
            paused (bool): Whether the game is paused
            score (int): Current score
            level (int): Current level
            lines_cleared (int): Total number of lines cleared
        """
        self.clear_screen()
        
        # Create a representation of the board
        board_repr = [[None for _ in range(board.width)] for _ in range(board.height)]
        
        # Add ghost tetromino first (so it appears below current tetromino)
        if ghost_tetromino and not game_over and not paused:
            board_repr = self.draw_tetromino(board_repr, ghost_tetromino, True)
            
        # Add current tetromino
        if current_tetromino:
            board_repr = self.draw_tetromino(board_repr, current_tetromino)
            
        # Add board contents
        for y in range(board.height):
            for x in range(board.width):
                if board_repr[y][x] is None:
                    board_repr[y][x] = board.grid[y][x]
                    
        # Convert board representation to string
        board_str = "┌" + "──" * board.width + "┐\n"
        for y in range(board.height):
            board_str += "│"
            for x in range(board.width):
                if board_repr[y][x] == "G":  # Ghost piece
                    board_str += self.draw_ghost_block()
                elif board_repr[y][x] is not None:
                    board_str += self.draw_block(True)
                else:
                    board_str += self.draw_block(False)
            board_str += "│\n"
        board_str += "└" + "──" * board.width + "┘"
        
        # Next piece preview
        next_piece_str = self.draw_next_piece(next_tetromino)
        
        # Game title
        title = "TERMINAL TETRIS"
        
        # Game stats
        stats = (
            f"Score: {format_score(score)}\n"
            f"Level: {level}\n"
            f"Lines: {lines_cleared}"
        )
        
        # Controls
        controls = (
            "Controls:\n"
            "←→↓: Move\n"
            "↑: Rotate\n"
            "Space: Drop\n"
            "P: Pause\n"
            "Q: Quit"
        )
        
        # Compose the UI
        ui_str = f"{title}\n\n{stats}\n\n{board_str}"
        
        # Add next piece preview to the right of the board
        board_lines = board_str.split('\n')
        next_piece_lines = next_piece_str.split('\n')
        control_lines = controls.split('\n')
        
        # Combine board and next piece preview side by side
        ui_lines = [title, "", stats, ""]
        for i in range(len(board_lines)):
            line = board_lines[i]
            if i < len(next_piece_lines):
                ui_lines.append(f"{line}    {next_piece_lines[i]}")
            elif i - len(next_piece_lines) < len(control_lines) and i >= len(next_piece_lines):
                ui_lines.append(f"{line}    {control_lines[i - len(next_piece_lines)]}")
            else:
                ui_lines.append(line)
                
        ui_str = "\n".join(ui_lines)
        
        # Add game over or pause screen in the middle of the board
        if game_over:
            game_over_str = self.draw_game_over()
            game_over_lines = game_over_str.split('\n')
            board_height = len(board_lines)
            start_row = (board_height - len(game_over_lines)) // 2
            
            for i, line in enumerate(game_over_lines):
                row = start_row + i
                if 0 <= row < len(ui_lines):
                    board_width = len(board_lines[0])
                    padding = (board_width - len(line)) // 2
                    ui_lines[row + 4] = line  # +4 for title, blank, stats, blank
            
            ui_str = "\n".join(ui_lines)
            
        elif paused:
            pause_str = self.draw_pause_screen()
            pause_lines = pause_str.split('\n')
            board_height = len(board_lines)
            start_row = (board_height - len(pause_lines)) // 2
            
            for i, line in enumerate(pause_lines):
                row = start_row + i
                if 0 <= row < len(ui_lines):
                    board_width = len(board_lines[0])
                    padding = (board_width - len(line)) // 2
                    ui_lines[row + 4] = line  # +4 for title, blank, stats, blank
            
            ui_str = "\n".join(ui_lines)
            
        print(ui_str)
        
    def update_score(self, score):
        """Update is not needed in the simple implementation"""
        pass
        
    def update_level(self, level):
        """Update is not needed in the simple implementation"""
        pass
        
    def update_lines(self, lines):
        """Update is not needed in the simple implementation"""
        pass 