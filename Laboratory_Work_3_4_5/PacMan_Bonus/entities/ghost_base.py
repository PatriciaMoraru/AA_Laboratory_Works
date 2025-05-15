import pygame
from maze_solver.pathfinding_utils import bfs_path, dfs_path, dijkstra_path
from setup.config import WIDTH, HEIGHT, TILE_WIDTH, TILE_HEIGHT
from entities.player import Player
import random
import math

def is_walkable(level, x, y):
    return level[y][x] == 1

def convert_level_to_bitmask_maze(level):
    rows, cols = len(level), len(level[0])
    bitmask_maze = [[0 for _ in range(cols)] for _ in range(rows)]

    for y in range(rows):
        for x in range(cols):
            if level[y][x] <= 2:
                if y > 0 and level[y - 1][x] <= 2:
                    bitmask_maze[y][x] |= 1  # N
                if y < rows - 1 and level[y + 1][x] <= 2:
                    bitmask_maze[y][x] |= 2  # S
                if x < cols - 1 and level[y][x + 1] <= 2:
                    bitmask_maze[y][x] |= 4  # E
                if x > 0 and level[y][x - 1] <= 2:
                    bitmask_maze[y][x] |= 8  # W
    return bitmask_maze


class BaseGhost:
    """Base ghost class with unified movement and state handling"""

    def __init__(self, x, y, speed, img, direction, ghost_id, level, screen,
                 powerup_ref, eaten_ghost_ref, level_source_ref, ghost_movement_ref):
        self.x_pos = x
        self.y_pos = y
        self.center_x = self.x_pos + TILE_WIDTH // 2
        self.center_y = self.y_pos + TILE_HEIGHT // 2
        if level_source_ref() == 'original':
            self.speed = speed
        else:
            self.speed = speed * 1.5  # increased speed for generated
        self.img = img
        self.direction = direction
        self.id = ghost_id
        self.level = level
        self.screen = screen
        self.powerup = powerup_ref
        self.eaten_ghost = eaten_ghost_ref
        self.level_source = level_source_ref
        self.ghost_movement = ghost_movement_ref

        # Pathfinding attributes
        self.path_algorithm = None  # Set externally (e.g., initialize_game)
        self.path = []
        self.path_step = 1

        # State control
        self.in_box = False
        self.is_returning_to_box = False
        self.turns = [False, False, False, False]
        self.target = (0, 0)
        self.rect = None
        self.last_direction_change = 0
        self.time_in_box = 0
        self.exit_timer = ghost_id * 180
        self.box_timer = 0
        self.force_exit = False
        self.timeout_counter = 0

        self.powerup_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/powerup.png'), (45, 45))
        self.dead_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/dead.png'), (45, 45))

        self.box_coords = {
            'left': 380,
            'right': 500,
            'top': 370,
            'bottom': 480,
            'entry_x': 440,
            'entry_y': 370
        }

        if self.level_source() == 'original':
            self.in_box = self.id != 0
        else:
            self.in_box = False

    def is_in_box(self):
        """Check if ghost is in the ghost box based on coordinates"""
        # Only applicable for original level
        if self.level_source() != 'original':
            return False

        return (self.box_coords['left'] < self.x_pos < self.box_coords['right'] and
                self.box_coords['top'] < self.y_pos < self.box_coords['bottom'])

    def check_valid_directions(self):
        """
        Check which directions the ghost can move based on surrounding walls
        """
        # Calculate the cell size based on level dimensions
        num1 = (HEIGHT - 50) // 32
        num2 = WIDTH // 30

        # Initialize directions as all blocked
        directions = [False, False, False, False]

        # Calculate current position in tile coordinates
        tile_x = int(self.center_x // num2)
        tile_y = int(self.center_y // num1)

        # Determine if ghost is in the box (only relevant for original level)
        in_box = False
        if self.level_source() == 'original':
            in_box = self.is_in_box()

        # If we're trying to exit the box and keep getting stuck, force upward movement
        if in_box and self.box_timer >= self.exit_timer:
            self.timeout_counter += 1
            if self.timeout_counter > 180:  # 3 seconds stuck
                # Force exit by always allowing upward movement in the box
                directions[2] = True
                return directions, in_box

        # Check if we're in a valid position in the level
        if 0 <= tile_y < len(self.level) and 0 <= tile_x < len(self.level[0]):
            # Check right direction (no wall to right)
            if tile_x + 1 < len(self.level[0]) and self.level[tile_y][tile_x + 1] < 3:
                directions[0] = True

            # Check left direction (no wall to left)
            if tile_x - 1 >= 0 and self.level[tile_y][tile_x - 1] < 3:
                directions[1] = True

            # Check up direction (no wall above)
            if tile_y - 1 >= 0 and self.level[tile_y - 1][tile_x] < 3:
                directions[2] = True

            # Check down direction (no wall below)
            if tile_y + 1 < len(self.level) and self.level[tile_y + 1][tile_x] < 3:
                directions[3] = True

            # FOR ORIGINAL MODE ONLY: Box Exit Special Handling
            if self.level_source() == 'original' and in_box:
                # For ghosts in the box, always allow them to move upward
                # to make exiting the box more reliable
                directions[2] = True

            # Special case: Gate handling (only for original level)
            if self.level_source() == 'original':
                # Look for the gate (value 9) in the level
                gate_found = False
                gate_x, gate_y = 0, 0

                for y in range(len(self.level)):
                    for x in range(len(self.level[0])):
                        if self.level[y][x] == 9:
                            gate_x, gate_y = x, y
                            gate_found = True
                            break
                    if gate_found:
                        break

                # If we found the gate, check if we're right below it and trying to exit
                if gate_found and in_box and self.box_timer >= self.exit_timer:
                    # If we're aligned with the gate horizontally, always allow up
                    if abs(self.center_x - (gate_x * num2 + num2 // 2)) < 20:
                        directions[2] = True  # Allow up

                # If we're above the gate and returning to box, allow down
                if gate_found and self.is_returning_to_box:
                    # If we're aligned with the gate horizontally and just above it
                    if abs(self.center_x - (gate_x * num2 + num2 // 2)) < 20 and tile_y == gate_y - 1:
                        directions[3] = True  # Allow down

        # Screen edge handling for left-right wrap
        if self.center_x < 20:
            directions[1] = True  # Allow moving left at screen edge
        if self.center_x > WIDTH - 20:
            directions[0] = True  # Allow moving right at screen edge

        return directions, in_box

    def handle_box_exit(self):
        """Handle ghost box exit logic (only for original level)"""
        if not self.in_box or self.level_source() != 'original':
            return False

        # Increment box timer
        self.box_timer += 1

        # Only allow exit after the appropriate delay based on ghost ID
        if self.box_timer < self.exit_timer:
            # Move back and forth while waiting
            if self.x_pos < 440 - 20:
                self.direction = 0  # Move right
                self.x_pos += 0.5
            elif self.x_pos > 440 + 20:
                self.direction = 1  # Move left
                self.x_pos -= 0.5
            else:
                # When centered, move up and down slightly
                if random.random() < 0.01:  # Occasionally change direction for natural movement
                    self.direction = random.choice([0, 1])

            # Update center
            self.center_x = self.x_pos + 22
            self.center_y = self.y_pos + 22
            return True

        # Time to exit - first, move to gate x-position
        gate_x = 440  # Default gate x-position

        # Look for the actual gate in the level
        gate_found = False
        num1 = (HEIGHT - 50) // 32
        num2 = WIDTH // 30

        for y in range(len(self.level)):
            for x in range(len(self.level[0])):
                if self.level[y][x] == 9:
                    gate_x = x * num2 + num2 // 2
                    gate_found = True
                    break
            if gate_found:
                break

        # Stage 1: Align horizontally with gate
        if abs(self.center_x - gate_x) > 10:
            if self.center_x < gate_x:
                self.direction = 0  # Right
                self.x_pos += self.speed
            else:
                self.direction = 1  # Left
                self.x_pos -= self.speed
        else:
            # Stage 2: Force upward movement
            self.x_pos = gate_x - 22  # Center ghost on gate
            self.direction = 2  # Up
            self.y_pos -= self.speed

            # Check if we've made it out
            if self.y_pos < self.box_coords['top'] - 5:
                self.in_box = False
                self.box_timer = 0
                self.timeout_counter = 0
                return False

        # Update center
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        return True

    def handle_return_to_box(self):
        """Handle ghost returning to box when eaten (only for original level)"""
        if not self.is_returning_to_box:
            return False

        # Generated levels have no box - just respawn ghost at center
        if self.level_source() != 'original':
            # Find a random valid path position
            valid_paths = []
            center_x = WIDTH // 2
            center_y = HEIGHT // 2

            # Find center area paths
            num1 = (HEIGHT - 50) // 32
            num2 = WIDTH // 30

            for y, row in enumerate(self.level):
                for x, cell in enumerate(row):
                    if cell == 1 or cell == 0:  # Path or empty space
                        screen_x = x * num2
                        screen_y = y * num1
                        # If near center
                        if (abs(screen_x - center_x) < 100 and
                                abs(screen_y - center_y) < 100):
                            valid_paths.append((screen_x, screen_y))

            # Pick a random position near center
            if valid_paths:
                pos = random.choice(valid_paths)
                self.x_pos = pos[0]
                self.y_pos = pos[1]
            else:
                # Fallback - just place in center
                self.x_pos = center_x - 22
                self.y_pos = center_y - 22

            self.center_x = self.x_pos + 22
            self.center_y = self.y_pos + 22
            self.is_returning_to_box = False
            return False

        # Original level - return to actual ghost box
        # Look for the gate position
        gate_pos = None
        num1 = (HEIGHT - 50) // 32
        num2 = WIDTH // 30

        # Find the gate by checking the level
        for y in range(len(self.level)):
            for x in range(len(self.level[0])):
                if self.level[y][x] == 9:  # Gate tile
                    gate_pos = (x * num2 + num2 // 2, y * num1)
                    break
            if gate_pos:
                break

        # If no gate found, use center top of box
        if not gate_pos:
            gate_pos = (WIDTH // 2, self.box_coords['top'])

        # Get the box center for final positioning
        box_center = (
            (self.box_coords['left'] + self.box_coords['right']) // 2,
            (self.box_coords['top'] + self.box_coords['bottom']) // 2
        )

        # Already in box?
        if self.is_in_box():
            self.in_box = True
            self.is_returning_to_box = False
            self.box_timer = 0

            # Move to center of box
            self.x_pos = box_center[0] - 22
            self.y_pos = box_center[1] - 22
            self.center_x = self.x_pos + 22
            self.center_y = self.y_pos + 22
            return True

        # Phase 1: Move to the gate x-position
        if abs(self.center_x - gate_pos[0]) > 10:
            if self.center_x < gate_pos[0]:
                self.direction = 0  # Right
                self.x_pos += self.speed * 2  # Move faster when returning
            else:
                self.direction = 1  # Left
                self.x_pos -= self.speed * 2
        # Phase 2: If above gate, move down to the gate
        elif self.center_y < gate_pos[1]:
            # Force x alignment
            self.x_pos = gate_pos[0] - 22

            self.direction = 3  # Down
            self.y_pos += self.speed * 2
        # Phase 3: Move into the box
        else:
            # We've reached the gate, now force movement down into box
            self.direction = 3  # Down
            self.y_pos += self.speed * 2

            # If we've moved well into the box, mark as in_box
            if self.center_y > gate_pos[1] + 30:
                self.in_box = True
                self.is_returning_to_box = False
                self.box_timer = 0

                # Center in the box
                self.x_pos = box_center[0] - 22
                self.y_pos = box_center[1] - 22

        # Update center
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        return True

    def calculate_target(self, player_x, player_y, player_direction, blinky_x=None, blinky_y=None):
        """
        Calculate the target position for the ghost based on its behavior.
        Each ghost subclass should override this method with its specific targeting behavior.
        """
        # Default to chase player directly
        return (player_x, player_y)

    def choose_direction(self):
        fallback_direction = self.direction

        if self.in_box and self.level_source() == 'original':
            if self.box_timer >= self.exit_timer and self.turns[2]:
                return 2
            return self.direction

        if self.is_returning_to_box:
            return self.direction

        opposite_direction = {0: 1, 1: 0, 2: 3, 3: 2}
        invalid_direction = opposite_direction[self.direction]

        if self.powerup() and not self.eaten_ghost()[self.id]:
            if random.random() < 0.05:
                valid_directions = [d for d in range(4) if self.turns[d] and d != invalid_direction]
                if valid_directions:
                    return random.choice(valid_directions)
            return self.direction

        best_distance = float('inf')
        best_direction = fallback_direction

        for d in range(4):
            if not self.turns[d] or d == invalid_direction:
                continue

            test_x, test_y = self.center_x, self.center_y
            if d == 0:  # Right
                test_x += TILE_WIDTH
            elif d == 1:  # Left
                test_x -= TILE_WIDTH
            elif d == 2:  # Up
                test_y -= TILE_HEIGHT
            elif d == 3:  # Down
                test_y += TILE_HEIGHT

            distance = ((test_x - self.target[0]) ** 2 + (test_y - self.target[1]) ** 2) ** 0.5
            if distance < best_distance:
                best_distance = distance
                best_direction = d

        return best_direction

    def move(self, target=None):
        """Updated movement using pathfinding if enabled"""
        self.target = target if target else self.target
        self.turns, self.in_box = self.check_valid_directions()

        # 1. Handle returning to box
        if self.is_returning_to_box:
            if self.handle_return_to_box():
                return self.x_pos, self.y_pos, self.direction

        # 2. If in box and original level, exit as normal
        if self.in_box and self.level_source() == 'original':
            if self.handle_box_exit():
                return self.x_pos, self.y_pos, self.direction

        # 3. Pathfinding mode logic
        if self.ghost_movement() == 'pathfinding':
            if self.level_source() != 'original':
                self.target = target if target else self.target
            num1 = (HEIGHT - 50) // 32
            num2 = WIDTH // 30

            start_tile = (int(self.center_x // num2), int(self.center_y // num1))
            end_tile = (int(self.target[0] // num2), int(self.target[1] // num1))

            if not (0 <= start_tile[0] < len(self.level[0]) and 0 <= start_tile[1] < len(self.level)):
                return self.x_pos, self.y_pos, self.direction
            if not (0 <= end_tile[0] < len(self.level[0]) and 0 <= end_tile[1] < len(self.level)):
                return self.x_pos, self.y_pos, self.direction

            if self.level[start_tile[1]][start_tile[0]] > 2 or self.level[end_tile[1]][end_tile[0]] > 2:
                return self.x_pos, self.y_pos, self.direction

            path_level = convert_level_to_bitmask_maze(self.level)

            try:
                self.path = self.path_algorithm(path_level, start_tile, end_tile, visualize=False)
                self.path_step = 1
            except Exception as e:
                print(f"[Ghost {self.id} pathfinding error]: {e}")
                return self.x_pos, self.y_pos, self.direction

            # Follow the path
            if self.path and self.path_step < len(self.path):
                next_tile = self.path[self.path_step]
                next_x = next_tile[0] * num2 + num2 // 2
                next_y = next_tile[1] * num1 + num1 // 2

                dx = next_x - self.center_x
                dy = next_y - self.center_y

                if abs(dx) > abs(dy):
                    if dx > 0 and self.turns[0]:
                        self.direction = 0  # Right
                    elif dx < 0 and self.turns[1]:
                        self.direction = 1  # Left
                else:
                    if dy < 0 and self.turns[2]:
                        self.direction = 2  # Up
                    elif dy > 0 and self.turns[3]:
                        self.direction = 3  # Down

                # Advance to next step if close
                if abs(self.center_x - next_x) < 4 and abs(self.center_y - next_y) < 4:
                    self.path_step += 1

                # Apply movement
                if self.direction == 0 and self.turns[0]:  # Right
                    self.x_pos += self.speed
                elif self.direction == 1 and self.turns[1]:  # Left
                    self.x_pos -= self.speed
                elif self.direction == 2 and self.turns[2]:  # Up
                    self.y_pos -= self.speed
                elif self.direction == 3 and self.turns[3]:  # Down
                    self.y_pos += self.speed

                self.center_x = self.x_pos + TILE_WIDTH // 2
                self.center_y = self.y_pos + TILE_HEIGHT // 2

                pygame.draw.circle(self.screen, (255, 0, 255), (int(self.center_x), int(self.center_y)), 4)

                return self.x_pos, self.y_pos, self.direction

        # 4. Fallback: Original chasing logic
        new_direction = self.choose_direction()

        # Force update if blocked or occasionally even when not
        if self.level_source() != 'original':
            if not self.turns[self.direction] or sum(self.turns) <= 1 or random.random() < 0.05:
                valid = [i for i, turn in enumerate(self.turns) if turn]
                if valid:
                    self.direction = random.choice(valid)
        else:
            if not self.turns[self.direction] or random.random() < 0.03:
                if self.turns[new_direction]:
                    self.direction = new_direction

        # Apply movement
        if self.direction == 0 and self.turns[0]:  # Right
            self.x_pos += self.speed
        elif self.direction == 1 and self.turns[1]:  # Left
            self.x_pos -= self.speed
        elif self.direction == 2 and self.turns[2]:  # Up
            self.y_pos -= self.speed
        elif self.direction == 3 and self.turns[3]:  # Down
            self.y_pos += self.speed

        self.center_x = self.x_pos + TILE_WIDTH // 2
        self.center_y = self.y_pos + TILE_HEIGHT // 2

        return self.x_pos, self.y_pos, self.direction

    # Add a helper function to the BaseGhost class to convert level to pathfinding format
    def convert_level_for_pathfinding(self):
        """Convert game level to format suitable for pathfinding algorithms"""
        # Create a temporary level with 1s for paths and 0s for walls
        temp_level = [[1 if cell <= 2 else 0 for cell in row] for row in self.level]

        # Create a mapping for the pathfinding algorithm
        path_level = [[0 for _ in range(len(self.level[0]))] for _ in range(len(self.level))]
        for y in range(len(temp_level)):
            for x in range(len(temp_level[0])):
                if temp_level[y][x] == 1:  # Path
                    # Check which directions are open
                    if y > 0 and temp_level[y - 1][x] == 1:  # North
                        path_level[y][x] |= 1
                    if y < len(temp_level) - 1 and temp_level[y + 1][x] == 1:  # South
                        path_level[y][x] |= 2
                    if x < len(temp_level[0]) - 1 and temp_level[y][x + 1] == 1:  # East
                        path_level[y][x] |= 4
                    if x > 0 and temp_level[y][x - 1] == 1:  # West
                        path_level[y][x] |= 8

        return path_level

    def draw(self):
        """Draw the ghost on the screen with appropriate image based on state"""
        # Choose the right image based on ghost state
        if self.powerup() and not self.eaten_ghost()[self.id]:
            # Powerup mode (frightened)
            ghost_image = self.powerup_img
        elif self.is_returning_to_box:
            # Dead/returning to box
            ghost_image = self.dead_img
        else:
            # Normal
            ghost_image = self.img

        # Draw the ghost
        self.screen.blit(ghost_image, (self.x_pos, self.y_pos))

        # Return the ghost's rectangle for collision detection
        return pygame.Rect(self.x_pos, self.y_pos, 45, 45)


class Blinky(BaseGhost):
    """Red ghost – chases directly"""
    def calculate_target(self, player_x, player_y, player_direction, blinky_x=None, blinky_y=None):
        return (player_x, player_y)


class Pinky(BaseGhost):
    """Pink ghost – 4 tiles ahead"""
    def calculate_target(self, player_x, player_y, player_direction, blinky_x=None, blinky_y=None):
        target_x, target_y = player_x, player_y
        if player_direction == 0:
            target_x += 80
        elif player_direction == 1:
            target_x -= 80
        elif player_direction == 2:
            target_y -= 80
            target_x -= 80  # classic bug
        elif player_direction == 3:
            target_y += 80
        return (target_x, target_y)


class Inky(BaseGhost):
    """Blue ghost – vector using Blinky"""
    def calculate_target(self, player_x, player_y, player_direction, blinky_x=None, blinky_y=None):
        if blinky_x is None or blinky_y is None:
            return (player_x, player_y)
        pivot_x, pivot_y = player_x, player_y
        if player_direction == 0:
            pivot_x += 40
        elif player_direction == 1:
            pivot_x -= 40
        elif player_direction == 2:
            pivot_y -= 40
            pivot_x -= 40
        elif player_direction == 3:
            pivot_y += 40
        vector_x = pivot_x - blinky_x
        vector_y = pivot_y - blinky_y
        return (blinky_x + 2 * vector_x, blinky_y + 2 * vector_y)


class Clyde(BaseGhost):
    """Orange ghost – close = flee, far = chase"""
    def calculate_target(self, player_x, player_y, player_direction, blinky_x=None, blinky_y=None):
        dist = ((player_x - self.x_pos) ** 2 + (player_y - self.y_pos) ** 2) ** 0.5
        if dist > 150:
            return (player_x, player_y)
        else:
            return (100, HEIGHT - 100)

