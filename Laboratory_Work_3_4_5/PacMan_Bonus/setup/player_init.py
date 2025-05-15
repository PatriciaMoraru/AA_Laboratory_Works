import random
from setup.config import WIDTH, HEIGHT, TILE_WIDTH, TILE_HEIGHT


def get_initial_positions(level_source, level):
    """
    Get the initial positions for player and ghosts based on level source.

    Args:
        level_source: 'original' or 'generated'
        level: The game level grid

    Returns:
        Tuple containing:
        - Player starting position (x, y)
        - Dictionary of ghost starting positions {'blinky': (x, y), etc.}
    """
    tile_width = WIDTH // 30
    tile_height = (HEIGHT - 50) // 32

    if level_source == 'generated':
        # Find all valid paths in the maze (cells with value 1 = dots)
        valid_paths = []
        for y, row in enumerate(level):
            for x, cell in enumerate(row):
                if cell == 1:  # Path with dot
                    # Convert to screen coordinates
                    screen_x = x * tile_width
                    screen_y = y * tile_height
                    valid_paths.append((screen_x, screen_y))

        if not valid_paths:
            raise ValueError("No valid paths found in the generated maze!")

        # Divide the maze into quadrants for better ghost distribution
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        # Create lists for different quadrants
        top_left = []
        top_right = []
        bottom_left = []
        bottom_right = []

        # Sort valid paths into quadrants
        for x, y in valid_paths:
            if x < center_x and y < center_y:
                top_left.append((x, y))
            elif x >= center_x and y < center_y:
                top_right.append((x, y))
            elif x < center_x and y >= center_y:
                bottom_left.append((x, y))
            else:
                bottom_right.append((x, y))

        # Ensure we have positions in each quadrant, otherwise use all paths
        if not top_left or not top_right or not bottom_left or not bottom_right:
            top_left = top_right = bottom_left = bottom_right = valid_paths

        # Calculate distance between two points
        def distance(pos1, pos2):
            return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

        # Pick a random position for the player, preferably in bottom half
        player_candidates = bottom_left + bottom_right if bottom_left or bottom_right else valid_paths
        player_pos = random.choice(player_candidates)

        # Get positions for ghosts, making sure they're far enough from player and each other
        min_distance = 200  # Minimum distance between characters

        def get_position_in_quadrant(quadrant, existing_positions):
            # Try to find a position at least min_distance away from existing positions
            attempts = 0
            while attempts < 50:  # Limit attempts to avoid infinite loop
                pos = random.choice(quadrant)
                # Check distance from player and other ghosts
                if all(distance(pos, other_pos) > min_distance for other_pos in [player_pos] + existing_positions):
                    return pos
                attempts += 1

            # If we can't find a good position after many attempts, just pick any
            return random.choice(quadrant)

        # Place each ghost in a different quadrant
        ghost_positions = []
        blinky_pos = get_position_in_quadrant(top_left, ghost_positions)
        ghost_positions.append(blinky_pos)

        inky_pos = get_position_in_quadrant(top_right, ghost_positions)
        ghost_positions.append(inky_pos)

        pinky_pos = get_position_in_quadrant(bottom_right, ghost_positions)
        ghost_positions.append(pinky_pos)

        clyde_pos = get_position_in_quadrant(bottom_left, ghost_positions)

        ghosts = {
            "blinky": blinky_pos,
            "inky": inky_pos,
            "pinky": pinky_pos,
            "clyde": clyde_pos
        }

    else:
        # Original Pac-Man positions
        player_pos = (450, 663)  # Bottom center
        ghosts = {
            "blinky": (440, 345),  # Start Blinky outside the box
            "inky": (440, 388),  # In the box
            "pinky": (440, 438),  # In the box
            "clyde": (440, 438)  # In the box
        }

    return player_pos, ghosts