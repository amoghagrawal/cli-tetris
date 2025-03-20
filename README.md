# Tetris Game

A beautiful terminal-based Tetris game built with Python and batgrl.

## Features

- Full-featured Tetris gameplay with standard controls
- Colorful, modern UI with box-drawing characters
- Proper game mechanics:
  - Piece rotation with wall kick
  - Ghost piece showing landing position
  - Hold piece functionality
  - Next piece preview
  - Score, level, and lines display
  - Increasing difficulty as you level up
- Pause and game over states
- High score tracking with persistent storage
- Multiple difficulty levels (Easy, Normal, Hard, Expert)
- Customizable controls
- Cross-platform support (Windows, macOS, Linux)

## Requirements

- Python 3.7+
- batgrl 0.44.1 (graphical terminal library)

## Installation

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the game: `python main.py`

## Command-Line Options

The game supports several command-line options:

```
python main.py [options]
```

Available options:
- `--level N`: Start at level N (1-10, default: 1)
- `--speed X`: Initial speed in seconds per drop (default: 1.0)
- `--fullscreen`: Start in fullscreen mode
- `--size WxH`: Set terminal size to width W and height H (e.g., 120x40)
- `--difficulty {easy,normal,hard,expert}`: Set game difficulty
- `--config FILE`: Use custom configuration file
- `--high-scores`: Show high scores and exit
- `--reset-scores`: Reset high scores
- `--help`: Show help message

Examples:
```
# Start at level 5
python main.py --level 5

# Start with faster initial speed
python main.py --speed 0.5

# Start in fullscreen mode at level 3
python main.py --fullscreen --level 3

# Set custom terminal size
python main.py --size 100x30

# Start with hard difficulty
python main.py --difficulty hard

# View high scores
python main.py --high-scores
```

## Controls

Default controls:
- **←, →**: Move piece left/right
- **↓**: Move piece down
- **↑**: Rotate piece
- **Space**: Hard drop (instantly place piece)
- **H**: Hold current piece
- **P**: Pause game
- **R**: Restart game when game over
- **Q**: Quit game

Alternative keyboard layouts are supported:
- **WASD controls**: W (rotate), A (left), S (down), D (right)
- **Vim-style**: K (rotate), J (left), I (down), L (right)

## Custom Controls

You can customize controls by editing the `tetris_config.json` file. The file is created automatically when you first run the game. The default settings look like this:

```json
{
  "controls": {
    "move_left": ["left", "a", "j"],
    "move_right": ["right", "d", "l"],
    "move_down": ["down", "s", "i"],
    "rotate": ["up", "w", "k"],
    "hard_drop": ["space"],
    "hold": ["h", "c"],
    "pause": ["p"],
    "quit": ["q", "escape"],
    "restart": ["r"]
  },
  "difficulty": "normal",
  "fullscreen": false
}
```

## Difficulty Levels

The game offers four difficulty levels:

- **Easy**: Slower initial speed, gradual progression
- **Normal**: Balanced speed and progression
- **Hard**: Faster initial speed, quicker progression
- **Expert**: Very fast speed and rapid progression

## High Scores

The game automatically saves your top 10 high scores to a file (`tetris_scores.json`). High scores include:
- Score
- Level reached
- Lines cleared
- Game duration
- Date/time

You can view high scores using `python main.py --high-scores` or reset them with `python main.py --reset-scores`.

## Project Structure

- `main.py`: Entry point and game loop
- `game.py`: Game logic and state management
- `ui.py`: User interface using batgrl
- `board.py`: Game board representation
- `tetromino.py`: Tetris piece definitions and behavior
- `constants.py`: Game constants and configuration
- `utils.py`: Helper functions for terminal handling, key mapping, and more
- `high_scores.py`: High score tracking and management
- `config.py`: Game configuration and custom controls

## Advanced Features

- **Terminal Size Detection**: Automatically detects terminal size for optimal display
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **FPS Limiting**: Consistent game speed across different systems
- **Custom Key Bindings**: Support for multiple keyboard layouts

## License

MIT
