import curses
import random
import time
import threading
from collections import deque
import os
import sys


class SnakeGame:
    def __init__(
        self,
    ):
        # Game dimensions
        self.width = 40
        self.height = 20

        # Game state
        self.snake = deque()
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.food = None
        self.score = 0
        self.game_over = False
        self.running = True

        # Game speed (delay between moves in milliseconds)
        self.delay = 150
        # Clear terminal
        os.system("cls" if os.name == "nt" else "clear")
        self.window_terminal_validity()

        # Initialize curses
        self.init_curses()

    def window_terminal_validity(self):
        # Re-check dimensions (in case terminal was resized)
        size = os.get_terminal_size()
        terminal_width = size.columns
        terminal_height = size.lines

        if terminal_height < self.height + 4 or terminal_width < self.width + 4:
            print(
                f"Terminal too small! Minimum required: "
                f"{self.height+4}x{self.width+4}, "
                f"Current: {terminal_height}x{terminal_width}"
            )
            print("Please expand terminal size")
            sys.exit(1)

    def init_curses(self):
        """Initialize the curses display"""
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        # Enable colors
        curses.start_color()
        curses.use_default_colors()

        # Define color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)  # Snake (green)
        curses.init_pair(2, curses.COLOR_RED, -1)  # Food (red)
        curses.init_pair(3, curses.COLOR_GREEN, -1)  # Border (dark green)
        curses.init_pair(4, curses.COLOR_WHITE, -1)  # Score text (white)
        curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Game over text (yellow)

        # Create game window with border
        self.game_win = curses.newwin(self.height + 2, self.width + 2, 2, 2)
        self.game_win.keypad(True)
        self.game_win.nodelay(True)

        # Get screen dimensions for score placement
        screen_height, screen_width = self.stdscr.getmaxyx()

    def draw_border(self):
        """Draw the dark green border around the game area"""
        self.game_win.attron(curses.color_pair(3) | curses.A_BOLD)
        self.game_win.border()
        self.game_win.attroff(curses.color_pair(3) | curses.A_BOLD)

    def init_snake(self):
        """Initialize the snake at the center of the screen"""
        center_x = self.width // 2
        center_y = self.height // 2

        # Snake starts with 3 segments
        self.snake = deque([(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)])

    def spawn_food(self):
        """Spawn food at a random empty location"""
        while True:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def draw_snake(self):
        """Draw the green snake"""
        for segment in self.snake:
            x, y = segment
            self.game_win.addch(y, x, "█", curses.color_pair(1) | curses.A_BOLD)

    def draw_food(self):
        """Draw the red food"""
        if self.food:
            x, y = self.food
            self.game_win.addch(y, x, "●", curses.color_pair(2) | curses.A_BOLD)

    def draw_score(self):
        """Draw the score at the bottom right outside the border"""
        score_text = f"Score: {self.score}"
        # Position: bottom right corner outside the game border
        score_y = 2 + self.height + 2  # Below the game window
        score_x = 2 + self.width + 2 - len(score_text)  # Right aligned

        self.stdscr.addstr(score_y, score_x, score_text, curses.color_pair(4) | curses.A_BOLD)

    def draw_instructions(self):
        """Draw game instructions"""
        instructions = ["Use WASD or Arrow Keys to move", "Press 'q' to quit", "Press 'r' to restart"]

        start_y = 2
        for i, instruction in enumerate(instructions):
            self.stdscr.addstr(start_y + i, 2 + self.width + 5, instruction, curses.color_pair(4))

    def move_snake(self):
        """Move the snake in the current direction"""
        head_x, head_y = self.snake[0]

        # Calculate new head position
        if self.direction == "UP":
            new_head = (head_x, head_y - 1)
        elif self.direction == "DOWN":
            new_head = (head_x, head_y + 1)
        elif self.direction == "LEFT":
            new_head = (head_x - 1, head_y)
        elif self.direction == "RIGHT":
            new_head = (head_x + 1, head_y)

        # Check for collisions
        if self.check_collision(new_head):
            self.game_over = True
            return

        # Add new head
        self.snake.appendleft(new_head)

        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
            # Increase speed slightly
            if self.delay > 50:
                self.delay = max(50, self.delay - 2)
        else:
            # Remove tail if no food eaten
            self.snake.pop()

    def check_collision(self, position):
        """Check if the snake collides with walls or itself"""
        x, y = position

        # Check wall collision
        if x <= 0 or x >= self.width - 1 or y <= 0 or y >= self.height - 1:
            return True

        # Check self collision
        if position in self.snake:
            return True

        return False

    def handle_input(self):
        """Handle keyboard input in a separate thread"""
        while self.running:
            try:
                key = self.game_win.getch()

                if key != -1:  # Key was pressed
                    # Convert to uppercase for consistency
                    if key in [ord("w"), ord("W"), curses.KEY_UP]:
                        if self.direction != "DOWN":
                            self.next_direction = "UP"
                    elif key in [ord("s"), ord("S"), curses.KEY_DOWN]:
                        if self.direction != "UP":
                            self.next_direction = "DOWN"
                    elif key in [ord("a"), ord("A"), curses.KEY_LEFT]:
                        if self.direction != "RIGHT":
                            self.next_direction = "LEFT"
                    elif key in [ord("d"), ord("D"), curses.KEY_RIGHT]:
                        if self.direction != "LEFT":
                            self.next_direction = "RIGHT"
                    elif key in [ord("q"), ord("Q")]:
                        self.running = False
                        self.game_over = True
                    elif key in [ord("r"), ord("R")] and self.game_over:
                        self.restart_game()

            except curses.error:
                pass

            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def restart_game(self):
        """Restart the game"""
        self.snake.clear()
        self.score = 0
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"
        self.game_over = False
        self.delay = 150
        self.init_snake()
        self.spawn_food()

    def draw_game_over(self):
        """Draw game over screen"""
        # Calculate center position
        center_y = self.height // 2
        center_x = self.width // 2

        game_over_text = "GAME OVER!"
        restart_text = "Press 'r' to restart or 'q' to quit"
        final_score_text = f"Final Score: {self.score}"

        # Draw game over messages
        self.game_win.addstr(
            center_y - 1, center_x - len(game_over_text) // 2, game_over_text, curses.color_pair(5) | curses.A_BOLD
        )
        self.game_win.addstr(center_y, center_x - len(final_score_text) // 2, final_score_text, curses.color_pair(4))
        self.game_win.addstr(center_y + 1, center_x - len(restart_text) // 2, restart_text, curses.color_pair(4))

    def draw_welcome(self):
        """Draw welcome screen"""
        welcome_text = "SNAKE GAME"
        start_text = "Press any key to start!"

        center_y = self.height // 2
        center_x = self.width // 2

        self.draw_border()
        self.game_win.addstr(
            center_y - 1, center_x - len(welcome_text) // 2, welcome_text, curses.color_pair(1) | curses.A_BOLD
        )
        self.game_win.addstr(center_y + 1, center_x - len(start_text) // 2, start_text, curses.color_pair(4))
        self.game_win.refresh()

        # Wait for key press
        self.game_win.nodelay(False)
        self.game_win.getch()
        self.game_win.nodelay(True)

    def update_display(self):
        """Update the game display"""
        # Clear the game area (not the border)
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.game_win.addch(y, x, " ")

        # Draw game elements
        self.draw_border()
        self.draw_snake()
        self.draw_food()

        if self.game_over:
            self.draw_game_over()

        # Update score and instructions
        self.stdscr.clear()
        self.draw_score()
        self.draw_instructions()

        # Refresh windows
        self.stdscr.refresh()
        self.game_win.refresh()

    def run(self):
        # Validate terminal size
        try:
            # Show welcome screen
            self.draw_welcome()

            # Initialize game
            self.init_snake()
            self.spawn_food()

            # Start input handling thread
            input_thread = threading.Thread(target=self.handle_input, daemon=True)
            input_thread.start()

            # Main game loop
            while self.running:
                if not self.game_over:
                    # Update direction
                    self.direction = self.next_direction

                    # Move snake
                    self.move_snake()

                # Update display
                self.update_display()

                # Game speed control
                time.sleep(self.delay / 1000.0)

        except KeyboardInterrupt:
            self.running = False
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up curses"""
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
