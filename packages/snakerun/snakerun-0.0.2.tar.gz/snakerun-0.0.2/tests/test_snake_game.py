from collections import deque
import random


def check_collision(position, snake, width, height):
    """Check if position collides with walls or snake body"""
    x, y = position

    # Check wall collision
    if x <= 0 or x >= width - 1 or y <= 0 or y >= height - 1:
        return True

    # Check self collision
    if position in snake:
        return True

    return False


def move_snake(snake, direction):
    """Move snake in given direction and return new head position"""
    head_x, head_y = snake[0]

    if direction == "UP":
        new_head = (head_x, head_y - 1)
    elif direction == "DOWN":
        new_head = (head_x, head_y + 1)
    elif direction == "LEFT":
        new_head = (head_x - 1, head_y)
    elif direction == "RIGHT":
        new_head = (head_x + 1, head_y)
    else:
        return None

    return new_head


def spawn_food(snake, width, height, max_attempts=100):
    """Spawn food at random empty location"""
    for _ in range(max_attempts):
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if (x, y) not in snake:
            return (x, y)
    return None


def is_valid_direction_change(current_direction, new_direction):
    """Check if direction change is valid (no reversing)"""
    opposite_directions = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

    return new_direction != opposite_directions.get(current_direction)


def calculate_new_delay(current_delay, min_delay=50, reduction=2):
    """Calculate new delay after eating food (speed increase)"""
    new_delay = current_delay - reduction
    return max(min_delay, new_delay)


# Test Case 1: Collision Detection
def test_wall_collision():
    """Test collision detection with game boundaries"""
    snake = deque([(20, 10), (19, 10), (18, 10)])
    width, height = 40, 20

    # Test collisions with each wall
    assert check_collision((0, 10), snake, width, height)  # Left wall
    assert check_collision((39, 10), snake, width, height)  # Right wall
    assert check_collision((20, 0), snake, width, height)  # Top wall
    assert check_collision((20, 19), snake, width, height)  # Bottom wall

    # Test valid position
    assert not check_collision((15, 10), snake, width, height)


def test_self_collision():
    """Test collision detection with snake body"""
    snake = deque([(20, 10), (19, 10), (18, 10), (17, 10)])
    width, height = 40, 20

    # Test collision with snake body
    assert check_collision((19, 10), snake, width, height)  # Body segment
    assert check_collision((18, 10), snake, width, height)  # Body segment

    # Test valid positions
    assert not check_collision((21, 10), snake, width, height)  # Empty space
    assert not check_collision((20, 11), snake, width, height)  # Empty space


# Test Case 2: Snake Movement
def test_snake_movement_directions():
    """Test snake movement in all four directions"""
    snake = deque([(20, 10), (19, 10), (18, 10)])

    # Test movement in each direction
    assert move_snake(snake, "RIGHT") == (21, 10)
    assert move_snake(snake, "LEFT") == (19, 10)
    assert move_snake(snake, "UP") == (20, 9)
    assert move_snake(snake, "DOWN") == (20, 11)

    # Test invalid direction
    assert move_snake(snake, "INVALID") is None


def test_snake_head_calculation():
    """Test that new head position is calculated correctly"""
    # Test from different starting positions
    snake1 = deque([(5, 5)])
    assert move_snake(snake1, "UP") == (5, 4)

    snake2 = deque([(0, 0)])  # Edge case
    assert move_snake(snake2, "RIGHT") == (1, 0)

    snake3 = deque([(39, 19)])  # Other edge
    assert move_snake(snake3, "LEFT") == (38, 19)


# Test Case 3: Food Spawning
def test_food_spawning_valid_positions():
    """Test that food spawns in valid game area"""
    snake = deque([(20, 10), (19, 10), (18, 10)])
    width, height = 40, 20

    # Test multiple food spawns
    for _ in range(10):
        food = spawn_food(snake, width, height)
        assert food is not None

        x, y = food
        # Food should be within boundaries
        assert 1 <= x <= width - 2
        assert 1 <= y <= height - 2

        # Food should not be on snake
        assert food not in snake


def test_food_spawning_no_valid_space():
    """Test food spawning when no space is available"""
    # Create a snake that fills most of the small game area
    width, height = 4, 4  # Very small game area
    snake = deque()

    # Fill most positions (leaving only walls)
    for x in range(1, width - 1):
        for y in range(1, height - 1):
            snake.append((x, y))

    # Should return None when no space available
    food = spawn_food(snake, width, height, max_attempts=10)
    assert food is None


# Test Case 4: Direction Validation
def test_valid_direction_changes():
    """Test valid direction changes"""
    # Test all valid direction changes
    assert is_valid_direction_change("UP", "LEFT")
    assert is_valid_direction_change("UP", "RIGHT")
    assert is_valid_direction_change("DOWN", "LEFT")
    assert is_valid_direction_change("DOWN", "RIGHT")
    assert is_valid_direction_change("LEFT", "UP")
    assert is_valid_direction_change("LEFT", "DOWN")
    assert is_valid_direction_change("RIGHT", "UP")
    assert is_valid_direction_change("RIGHT", "DOWN")


def test_invalid_direction_changes():
    """Test invalid direction changes (reversing)"""
    # Test opposite direction changes (should be invalid)
    assert not is_valid_direction_change("UP", "DOWN")
    assert not is_valid_direction_change("DOWN", "UP")
    assert not is_valid_direction_change("LEFT", "RIGHT")
    assert not is_valid_direction_change("RIGHT", "LEFT")


def test_same_direction_change():
    """Test continuing in same direction"""
    # Continuing in same direction should be valid
    assert is_valid_direction_change("UP", "UP")
    assert is_valid_direction_change("DOWN", "DOWN")
    assert is_valid_direction_change("LEFT", "LEFT")
    assert is_valid_direction_change("RIGHT", "RIGHT")


# Test Case 5: Game Speed Control
def test_speed_increase_calculation():
    """Test game speed increase after eating food"""
    # Test normal speed increase
    assert calculate_new_delay(150, min_delay=50, reduction=2) == 148
    assert calculate_new_delay(100, min_delay=50, reduction=2) == 98
    assert calculate_new_delay(60, min_delay=50, reduction=2) == 58


def test_minimum_speed_limit():
    """Test that speed doesn't go below minimum"""
    # Test minimum speed enforcement
    assert calculate_new_delay(52, min_delay=50, reduction=2) == 50
    assert calculate_new_delay(50, min_delay=50, reduction=2) == 50
    assert calculate_new_delay(45, min_delay=50, reduction=2) == 50


def test_speed_with_different_parameters():
    """Test speed calculation with different parameters"""
    # Test with different reduction amounts
    assert calculate_new_delay(100, min_delay=30, reduction=5) == 95
    assert calculate_new_delay(100, min_delay=30, reduction=10) == 90

    # Test with different minimum delays
    assert calculate_new_delay(40, min_delay=35, reduction=10) == 35
    assert calculate_new_delay(25, min_delay=20, reduction=3) == 22


# Integration test combining multiple functions
def test_game_sequence():
    """Test a sequence of game operations"""
    # Initial setup
    snake = deque([(20, 10), (19, 10), (18, 10)])
    width, height = 40, 20
    direction = "RIGHT"
    delay = 150

    # Move snake
    new_head = move_snake(snake, direction)
    assert new_head == (21, 10)

    # Check for collision (should be safe)
    collision = check_collision(new_head, snake, width, height)
    assert not collision

    # Spawn food
    food = spawn_food(snake, width, height)
    assert food is not None

    # Test direction change
    new_direction = "UP"
    valid_change = is_valid_direction_change(direction, new_direction)
    assert valid_change

    # Calculate new delay (simulate eating food)
    new_delay = calculate_new_delay(delay)
    assert new_delay == 148


if __name__ == "__main__":
    # Run specific test
    print("Running functional tests...")

    test_wall_collision()
    test_snake_movement_directions()
    test_food_spawning_valid_positions()
    test_valid_direction_changes()
    test_speed_increase_calculation()
    test_game_sequence()

    print("All tests passed!")
