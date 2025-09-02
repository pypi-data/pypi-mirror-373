# snakerun/cli.py
from snakerun import SnakeGame


def main():
    try:
        game = SnakeGame()
        game.run()  # or whatever starts your game
    except Exception as e:
        print(f"{e}")  # Only prints your custom exception message


if __name__ == "__main__":
    main()
