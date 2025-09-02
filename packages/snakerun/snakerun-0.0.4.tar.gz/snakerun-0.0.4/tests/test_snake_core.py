from collections import deque
from snakerun import SnakeGame    
import os
import pytest
import sys
 
def set_terminal_small(rows=15, cols=40):
    if sys.platform.startswith("win"):
        # Windows: use 'mode' command
        os.system(f"mode con: cols={cols} lines={rows}")
    else:
        # Linux/macOS: ANSI escape
        os.system(f"printf '\\e[8;{rows};{cols}t'")


class TestSnakeGame:

    def setup_method(self):
        """Initialize a fresh game before each test"""
        os.system(r"printf '\e[8;40;100t'")
        self.game = SnakeGame()
        # # Reset interactive stuff (we won’t run curses UI in tests)
        # self.game.snake = deque()
        # self.game.food = None
        # self.game.score = 0
        # self.game.game_over = False
        # self.game.running = True
        # self.game.direction = "RIGHT"
        # self.game.next_direction = "RIGHT"

    def teardown_method(self, method):
        del self.game


    def test_init_snake(self):
        """Snake should start at center with 3 segments"""
        self.game.init_snake()
        assert len(self.game.snake) == 3
        head_x, head_y = self.game.snake[0]
        assert (head_x, head_y) == (self.game.width // 2, self.game.height // 2)

    def test_spawn_food_not_on_snake(self):
        """Food should not spawn on the snake body"""
        self.game.init_snake()
        self.game.spawn_food()
        assert self.game.food is not None
        assert self.game.food not in self.game.snake

    def test_move_snake_forward(self):
        """Snake should move right when direction=RIGHT"""
        self.game.init_snake()
        head_before = self.game.snake[0]
        self.game.move_snake()
        head_after = self.game.snake[0]
        assert head_after[0] == head_before[0] + 1  # moved right
        assert head_after[1] == head_before[1]

    def test_snake_eats_food_and_grows(self):
        """When snake eats food, score increases and length grows"""
        self.game.init_snake()
        head_x, head_y = self.game.snake[0]
        self.game.food = (head_x + 1, head_y)  # Place food directly ahead
        initial_length = len(self.game.snake)

        self.game.move_snake()

        assert len(self.game.snake) == initial_length + 1
        assert self.game.score == 1
        assert self.game.food is not None  # Respawned

    def test_snake_collision_with_wall(self):
        """Snake should set game_over when hitting a wall"""
        self.game.snake = deque([(self.game.width - 2, 5)])  # near right wall
        self.game.direction = "RIGHT"
        self.game.move_snake()
        assert self.game.game_over is True

    def test_snake_collision_with_itself(self):
        """Snake should die when colliding with itself"""
        # Manually create self-collision shape
        self.game.snake = deque([(5, 5), (4, 5), (3, 5), (3, 6), (4, 6), (5, 6)])
        self.game.direction = "UP"  # head at (5,5) moves into (5,4) -> no crash
        self.game.snake.appendleft((5, 6))  # force head into body
        assert self.game.check_collision((5, 6)) is True

    def test_restart_game_resets_state(self):
        """Restarting should reset score, snake, and game_over flag"""
        self.game.init_snake()
        self.game.score = 10
        self.game.game_over = True
        self.game.restart_game()

        assert self.game.score == 0
        assert self.game.game_over is False
        assert len(self.game.snake) == 3
        assert self.game.food is not None


class TestSmallTerminalSnakegame:
    def setup_method(self):
        """Initialize a fresh game with small terminal"""
        set_terminal_small(rows=15, cols=40)    
        
    def test_window_terminal_validity_print(self):

        with pytest.raises(Exception) as exc_info:
            SnakeGame()
        assert "Terminal too small" in str(exc_info.value)
        assert "Minimum required: 24x44" in str(exc_info.value)
