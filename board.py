from constants import BOARD_WIDTH, BOARD_HEIGHT, COLORS

class Board:
    def __init__(self, width=BOARD_WIDTH, height=BOARD_HEIGHT):
        """
        Initialize a new game board
        
        Args:
            width (int): Board width in cells
            height (int): Board height in cells
        """
        self.width = width
        self.height = height
        self.reset()
    
    def reset(self):
        """Reset the board to an empty state"""
        # Create an empty grid (None represents empty cells)
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        
    def is_valid_position(self, tetromino):
        """
        Check if the tetromino is in a valid position (not colliding with walls or other pieces)
        
        Args:
            tetromino (Tetromino): The tetromino to check
            
        Returns:
            bool: True if position is valid, False otherwise
        """
        if not tetromino:
            return False
            
        for x, y in tetromino.get_coords():
            # Check if out of bounds
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            
            # Check if position is already occupied
            if y >= 0 and self.grid[y][x] is not None:
                return False
                
        return True
    
    def place_tetromino(self, tetromino):
        """
        Place a tetromino on the board permanently
        
        Args:
            tetromino (Tetromino): The tetromino to place
            
        Returns:
            bool: True if placed successfully, False otherwise
        """
        if not self.is_valid_position(tetromino):
            return False
            
        for x, y in tetromino.get_coords():
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = tetromino.shape_type
        
        return True
    
    def clear_lines(self):
        """
        Clear any completed lines and return the number of lines cleared
        
        Returns:
            int: Number of lines cleared
        """
        lines_cleared = 0
        y = self.height - 1
        
        while y >= 0:
            # Check if line is complete
            if all(cell is not None for cell in self.grid[y]):
                # Remove the line
                self.grid.pop(y)
                # Add empty line at the top
                self.grid.insert(0, [None] * self.width)
                lines_cleared += 1
                # Don't decrement y since we need to check the new line at this position
            else:
                y -= 1
                
        return lines_cleared
    
    def is_game_over(self):
        """
        Check if the game is over (blocks in the top row)
        
        Returns:
            bool: True if game is over, False otherwise
        """
        # Game is over if there are any blocks in the top row
        return any(cell is not None for cell in self.grid[0])
    
    def get_cell_color(self, x, y):
        """
        Get the color of a cell at the given coordinates
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            str: Color hex code or None if empty
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return COLORS['EMPTY']
            
        cell_type = self.grid[y][x]
        return COLORS[cell_type] if cell_type else COLORS['EMPTY']
    
    def get_cell(self, x, y):
        """
        Get the contents of a cell at the given coordinates
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            str or None: Cell content (tetromino type) or None if empty
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
            
        return self.grid[y][x]
    
    def get_filled_rows(self):
        """
        Get list of rows that are filled (ready to be cleared)
        
        Returns:
            list: Indices of filled rows
        """
        filled_rows = []
        for y in range(self.height):
            if all(cell is not None for cell in self.grid[y]):
                filled_rows.append(y)
        
        return filled_rows
    
    def row_is_empty(self, row_index):
        """
        Check if a row is completely empty
        
        Args:
            row_index (int): Index of the row to check
            
        Returns:
            bool: True if row is empty, False otherwise
        """
        if not (0 <= row_index < self.height):
            return False
            
        return all(cell is None for cell in self.grid[row_index])
    
    def count_filled_cells(self):
        """
        Count the number of filled cells on the board
        
        Returns:
            int: Number of filled cells
        """
        count = 0
        for row in self.grid:
            for cell in row:
                if cell is not None:
                    count += 1
        
        return count
    
    def get_highest_filled_row(self):
        """
        Get the index of the highest (topmost) row that contains filled cells
        
        Returns:
            int: Index of the highest filled row, or -1 if board is empty
        """
        for y in range(self.height):
            if any(cell is not None for cell in self.grid[y]):
                return y
        
        return -1  # Board is empty
    
    def print_board(self):
        """Print ASCII representation of the board (for debugging)"""
        for row in self.grid:
            line = ""
            for cell in row:
                if cell is None:
                    line += ". "
                else:
                    line += cell + " "
            print(line) 