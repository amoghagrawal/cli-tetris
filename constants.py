# Game Board Constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 1

# Game Speed
INITIAL_SPEED = 1.0  # seconds per tick
SPEED_INCREASE = 0.05  # gradual speed increase per drop
LEVEL_SPEED_INCREASE = 0.1  # speed increase per level
MIN_SPEED = 0.05  # minimum speed cap

# Scoring
POINTS_SINGLE = 100  # points for clearing 1 line
POINTS_DOUBLE = 300  # points for clearing 2 lines
POINTS_TRIPLE = 500  # points for clearing 3 lines
POINTS_TETRIS = 800  # points for clearing 4 lines
LINES_PER_LEVEL = 10  # lines needed to advance to next level

# Colors
COLORS = {
    'I': '#00FFFF',  # Cyan
    'J': '#0000FF',  # Blue
    'L': '#FF7F00',  # Orange
    'O': '#FFFF00',  # Yellow
    'S': '#00FF00',  # Green
    'T': '#800080',  # Purple
    'Z': '#FF0000',  # Red
    'EMPTY': '#000000',  # Black
    'BORDER': '#FFFFFF',  # White
    'GHOST': '#333333',  # Dark Gray
    'BACKGROUND': '#111111',  # Dark background
    'TEXT': '#CCCCCC',  # Light gray text
}

# Tetromino Shapes
# Each shape has 4 rotations defined as relative coordinates
SHAPES = {
    # I tetromino - long piece
    'I': [[(0, 0), (0, 1), (0, 2), (0, 3)],
          [(0, 0), (1, 0), (2, 0), (3, 0)],
          [(0, 0), (0, 1), (0, 2), (0, 3)],
          [(0, 0), (1, 0), (2, 0), (3, 0)]],
          
    # J tetromino - left L piece
    'J': [[(0, 0), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (0, 1), (1, 0), (2, 0)],
          [(0, 0), (0, 1), (0, 2), (1, 2)],
          [(0, 1), (1, 1), (2, 0), (2, 1)]],
          
    # L tetromino - right L piece
    'L': [[(0, 0), (0, 1), (0, 2), (1, 0)],
          [(0, 0), (1, 0), (2, 0), (2, 1)],
          [(0, 2), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (0, 1), (1, 1), (2, 1)]],
          
    # O tetromino - square piece
    'O': [[(0, 0), (0, 1), (1, 0), (1, 1)],
          [(0, 0), (0, 1), (1, 0), (1, 1)],
          [(0, 0), (0, 1), (1, 0), (1, 1)],
          [(0, 0), (0, 1), (1, 0), (1, 1)]],
          
    # S tetromino - S-shaped piece
    'S': [[(0, 1), (0, 2), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (1, 1), (2, 1)],
          [(0, 1), (0, 2), (1, 0), (1, 1)],
          [(0, 0), (1, 0), (1, 1), (2, 1)]],
          
    # T tetromino - T-shaped piece
    'T': [[(0, 1), (1, 0), (1, 1), (1, 2)],
          [(0, 0), (1, 0), (1, 1), (2, 0)],
          [(0, 0), (0, 1), (0, 2), (1, 1)],
          [(0, 1), (1, 0), (1, 1), (2, 1)]],
          
    # Z tetromino - Z-shaped piece
    'Z': [[(0, 0), (0, 1), (1, 1), (1, 2)],
          [(0, 1), (1, 0), (1, 1), (2, 0)],
          [(0, 0), (0, 1), (1, 1), (1, 2)],
          [(0, 1), (1, 0), (1, 1), (2, 0)]]
}

# Starting positions
START_X = BOARD_WIDTH // 2 - 1  # start position X (center of board)
START_Y = 0  # start position Y (top of board)

# Game mechanics
WALL_KICK_ATTEMPTS = 3  # number of positions to try when rotating near a wall

# Key Bindings
KEY_QUIT = 'q'
KEY_PAUSE = 'p'
KEY_RESTART = 'r'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
KEY_DOWN = 'down'
KEY_DROP = 'space'
KEY_ROTATE = 'up'

# UI Constants
PREVIEW_WIDTH = 6
PREVIEW_HEIGHT = 6
INFO_PADDING = 3  # padding between board and info displays 