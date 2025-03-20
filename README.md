# CLI Tetris

A command-line implementation of the classic Tetris game using the batgrl library.

## Features

- Classic Tetris gameplay
- Terminal-based UI with colors
- Score and level tracking
- Increasing difficulty as you level up
- Next piece preview
- Game over detection

## Requirements

- Python 3.7+
- batgrl 0.6.1+

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cli-tetris.git
   cd cli-tetris
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## How to Play

Run the game:
```
python main.py
```

### Controls

- **Arrow Left/Right**: Move tetromino horizontally
- **Arrow Down**: Move tetromino down
- **Arrow Up**: Rotate tetromino
- **Space**: Hard drop (instantly drops the tetromino)
- **P**: Pause/resume the game
- **Q**: Quit the game
- **R**: Restart the game (when game over)

## Project Structure

- **main.py**: Entry point
- **game.py**: Main game logic
- **board.py**: Game board state and mechanics
- **tetromino.py**: Tetromino pieces definition and behavior
- **ui.py**: Terminal user interface components
- **constants.py**: Game constants and configuration
- **utils.py**: Helper functions

## License

MIT
