import random
from constants import COLORS, SHAPES, START_X, START_Y


class Tetromino:
    def __init__(self, shape_type=None, x=0, y=0, rotation=0):
        """
        Initialize a new tetromino piece
        
        Args:
            shape_type (str): One of 'I', 'J', 'L', 'O', 'S', 'T', 'Z'
            x (int): Initial x position
            y (int): Initial y position
            rotation (int): Initial rotation (0-3)
        """
        self.shape_type = shape_type
        self.x = x
        self.y = y
        self.rotation = rotation
        self.color = COLORS[shape_type] if shape_type else None
    
    @classmethod
    def random(cls, x=START_X, y=START_Y):
        """
        Create a random tetromino at the specified position
        
        Args:
            x (int): Initial x position
            y (int): Initial y position
            
        Returns:
            Tetromino: A new random tetromino
        """
        shape_type = random.choice(list(SHAPES.keys()))
        return cls(shape_type=shape_type, x=x, y=y)
    
    def get_coords(self):
        """
        Return the current absolute coordinates of the tetromino blocks
        
        Returns:
            list: List of (x, y) tuples representing block positions
        """
        shape = SHAPES[self.shape_type][self.rotation]
        return [(self.x + dx, self.y + dy) for dx, dy in shape]
    
    def rotate_clockwise(self):
        """
        Rotate the tetromino clockwise
        
        Returns:
            Tetromino: Self for method chaining
        """
        self.rotation = (self.rotation + 1) % 4
        return self
    
    def rotate_counterclockwise(self):
        """
        Rotate the tetromino counterclockwise
        
        Returns:
            Tetromino: Self for method chaining
        """
        self.rotation = (self.rotation - 1) % 4
        return self
    
    def move(self, dx, dy):
        """
        Move the tetromino by the given delta
        
        Args:
            dx (int): Horizontal movement (negative=left, positive=right)
            dy (int): Vertical movement (positive=down)
            
        Returns:
            Tetromino: Self for method chaining
        """
        self.x += dx
        self.y += dy
        return self
    
    def move_left(self):
        """
        Move the tetromino one cell to the left
        
        Returns:
            Tetromino: Self for method chaining
        """
        return self.move(-1, 0)
    
    def move_right(self):
        """
        Move the tetromino one cell to the right
        
        Returns:
            Tetromino: Self for method chaining
        """
        return self.move(1, 0)
    
    def move_down(self):
        """
        Move the tetromino one cell down
        
        Returns:
            Tetromino: Self for method chaining
        """
        return self.move(0, 1)
    
    def clone(self):
        """
        Create a copy of this tetromino
        
        Returns:
            Tetromino: A new tetromino with the same properties
        """
        return Tetromino(
            shape_type=self.shape_type,
            x=self.x,
            y=self.y,
            rotation=self.rotation
        )
    
    def get_ghost_position(self, board):
        """
        Calculate the position where the tetromino would land if dropped
        
        Args:
            board: The game board
            
        Returns:
            Tetromino: A ghost tetromino showing the landing position
        """
        ghost = self.clone()
        
        # Move down until collision
        while board.is_valid_position(ghost):
            ghost.move_down()
        
        # Move back up one step
        ghost.move(0, -1)
        
        return ghost
    
    @property
    def width(self):
        """
        Get the width of the tetromino in its current rotation
        
        Returns:
            int: Width in cells
        """
        coords = self.get_coords()
        min_x = min(x for x, _ in coords)
        max_x = max(x for x, _ in coords)
        return max_x - min_x + 1
    
    @property
    def height(self):
        """
        Get the height of the tetromino in its current rotation
        
        Returns:
            int: Height in cells
        """
        coords = self.get_coords()
        min_y = min(y for _, y in coords)
        max_y = max(y for _, y in coords)
        return max_y - min_y + 1 