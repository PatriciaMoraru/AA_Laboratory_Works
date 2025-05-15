from board import boards
import pickle
import pygame
import math
import copy
import os
from setup.level_loader import load_level
from setup.player_init import get_initial_positions
from maze_maker.kruskal_algorithm import generate_and_save_tile_map
from setup.config import WIDTH, HEIGHT
from entities.player import Player
from entities.ghost_base import Blinky, Pinky, Inky, Clyde
from maze_solver.pathfinding_utils import bfs_path, dfs_path, dijkstra_path

# Initialize pygame
pygame.init()

# Constants
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Pac-Man")
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
title_font = pygame.font.Font('freesansbold.ttf', 30)
color = 'blue'
PI = math.pi

# Load images
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45)))

blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))
pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (45, 45))
inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (45, 45))
clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (45, 45))
spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))

# Game variables
game_menu = True
level_source = None
level = None
player = None
blinky = None
inky = None
pinky = None
clyde = None
counter = 0
flicker = False
turns_allowed = [False, False, False, False]
score = 0
powerup = False
power_counter = 0
eaten_ghost = [False, False, False, False]
targets = [(0, 0)] * 4
moving = False
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = False
game_won = False
ghost_movement = "original"  # Default to original movement
path_alg = 'bfs'

def initialize_game():
    """Initialize or reset the game state"""
    global player, blinky, inky, pinky, clyde, score, lives
    global eaten_ghost, level, game_over, game_won, startup_counter, moving, power_counter, powerup

    print(f"Initializing game with level_source={level_source}, ghost_movement={ghost_movement}")  # Debug print

    if level_source == 'generated':
        try:
            generate_and_save_tile_map("maze_maker/kruskal_tile_map.pkl")
            with open("maze_maker/kruskal_tile_map.pkl", "rb") as f:
                level = pickle.load(f)
            print("Successfully loaded generated maze")
        except Exception as e:
            print(f"Error loading generated maze: {e}")
            level = copy.deepcopy(boards)  # Fallback to original level
    else:
        level = copy.deepcopy(boards)
        print("Using original level")

        # Remove top of ghost box if present
        center_x = len(level[0]) // 2
        center_y = len(level) // 2
        gate_found = False
        for y in range(len(level)):
            for x in range(len(level[0])):
                if level[y][x] == 9:
                    gate_y, gate_x = y, x
                    gate_found = True
                    for dy in range(-4, 2):
                        ny = gate_y + dy
                        if 0 <= ny < len(level):
                            for dx in range(-1, 2):
                                nx = gate_x + dx
                                if 0 <= nx < len(level[0]):
                                    level[ny][nx] = 0
                    break
            if gate_found:
                break
        if not gate_found:
            gate_y = center_y - 2
            for x in range(center_x - 3, center_x + 4):
                if 0 <= x < len(level[0]):
                    if level[gate_y][x] in [4, 5, 6, 9]:
                        level[gate_y][x] = 0

    # Get starting positions
    try:
        (start_x, start_y), ghost_starts = get_initial_positions(level_source, level)
        print(f"Player starting position: ({start_x}, {start_y})")

        player = Player(start_x, start_y, 2, player_images)

        # Set ghost positions
        blinky_x, blinky_y = ghost_starts["blinky"]
        inky_x, inky_y = ghost_starts["inky"]
        pinky_x, pinky_y = ghost_starts["pinky"]
        clyde_x, clyde_y = ghost_starts["clyde"]

        print(f"Ghost positions - Blinky: ({blinky_x}, {blinky_y}), Inky: ({inky_x}, {inky_y}), "
              f"Pinky: ({pinky_x}, {pinky_y}), Clyde: ({clyde_x}, {clyde_y})")

        # Resolve algorithm function
        if path_alg == 'bfs':
            algorithm_func = bfs_path
        elif path_alg == 'dfs':
            algorithm_func = dfs_path
        elif path_alg == 'dijkstra':
            algorithm_func = dijkstra_path
        else:
            algorithm_func = bfs_path  # fallback

        # Create ghost instances with algorithm assignment
        blinky = Blinky(blinky_x, blinky_y, 1, blinky_img, 0, 0, level, screen,
                        lambda: powerup, lambda: eaten_ghost, lambda: level_source, lambda: ghost_movement)
        inky = Inky(inky_x, inky_y, 1, inky_img, 2, 1, level, screen,
                    lambda: powerup, lambda: eaten_ghost, lambda: level_source, lambda: ghost_movement)
        pinky = Pinky(pinky_x, pinky_y, 1, pinky_img, 2, 2, level, screen,
                      lambda: powerup, lambda: eaten_ghost, lambda: level_source, lambda: ghost_movement)
        clyde = Clyde(clyde_x, clyde_y, 1, clyde_img, 2, 3, level, screen,
                      lambda: powerup, lambda: eaten_ghost, lambda: level_source, lambda: ghost_movement)

        # Assign algorithm function to all ghosts
        for ghost in [blinky, inky, pinky, clyde]:
            ghost.path_algorithm = algorithm_func

        # Reset game state
        score = 0
        lives = 3
        power_counter = 0
        powerup = False
        startup_counter = 0
        moving = False
        eaten_ghost = [False, False, False, False]
        game_over = game_won = False

        # Ghost box logic
        if level_source == 'original':
            blinky.in_box = False
            inky.in_box = True
            pinky.in_box = True
            clyde.in_box = True

            inky.x_pos = 440 - 30
            inky.center_x = inky.x_pos + 22
            pinky.x_pos = 440
            pinky.center_x = pinky.x_pos + 22
            clyde.x_pos = 440 + 30
            clyde.center_x = clyde.x_pos + 22
        else:
            for ghost in [blinky, inky, pinky, clyde]:
                ghost.in_box = False

        for ghost in [blinky, inky, pinky, clyde]:
            if ghost:
                ghost.turns, ghost.in_box = ghost.check_valid_directions()
                print(f"Ghost {ghost.id} can move: {ghost.turns}, In box: {ghost.in_box}")

        print("Game initialization complete!")
    except Exception as e:
        print(f"Error during game initialization: {e}")
        import traceback
        traceback.print_exc()


def draw_board_original():
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)

    for i in range(len(level)):
        for j in range(len(level[i])):
            tile = level[i][j]

            # Pellets
            if tile == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + num2 // 2, i * num1 + num1 // 2), 4)
            elif tile == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + num2 // 2, i * num1 + num1 // 2), 10)

            # Walls (full classic style)
            if tile == 3:  # Vertical
                pygame.draw.line(screen, color, (j * num2 + num2 // 2, i * num1),
                                 (j * num2 + num2 // 2, i * num1 + num1), 3)
            elif tile == 4:  # Horizontal
                pygame.draw.line(screen, color, (j * num2, i * num1 + num1 // 2),
                                 (j * num2 + num2, i * num1 + num1 // 2), 3)
            elif tile == 5:  # Top-right corner
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            elif tile == 6:  # Top-left corner
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],
                                PI / 2, PI, 3)
            elif tile == 7:  # Bottom-left corner
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1],
                                PI, 3 * PI / 2, 3)
            elif tile == 8:  # Bottom-right corner
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1],
                                3 * PI / 2, 2 * PI, 3)
            elif tile == 9:  # Gate
                pygame.draw.line(screen, 'white',
                                 (j * num2 + 5, i * num1 + num1 // 2),
                                 (j * num2 + num2 - 5, i * num1 + num1 // 2), 2)


def draw_board_generated():
    """Draw the generated maze with polished solid blue walls and white pellets."""
    tile_height = (HEIGHT - 50) // 32
    tile_width = WIDTH // 30
    PELLET_RADIUS = 3
    POWER_RADIUS = 8

    for i in range(len(level)):
        for j in range(len(level[i])):
            tile = level[i][j]
            x = j * tile_width
            y = i * tile_height

            if tile == 4:
                # Outer darker border
                pygame.draw.rect(screen, (0, 0, 180), pygame.Rect(x, y, tile_width, tile_height))
                # Inner brighter fill
                pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(x + 2, y + 2, tile_width - 4, tile_height - 4))

            elif tile == 1:
                pygame.draw.circle(screen, 'white',
                                   (x + tile_width // 2, y + tile_height // 2), PELLET_RADIUS)

            elif tile == 2 and not flicker:
                pygame.draw.circle(screen, 'white',
                                   (x + tile_width // 2, y + tile_height // 2), POWER_RADIUS)


def draw_misc():
    """Draw score, lives, power indicator, and game state messages"""
    # Score
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))

    # Power indicator
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)

    # Lives
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))

    # Game over
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (100, 300))

    # Victory
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (100, 300))


def draw_menu():
    """Draw the main menu for level and mode selection"""
    screen.fill('black')

    # Title
    title_text = title_font.render('PAC-MAN', True, 'yellow')
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    # Level selection
    level_text = font.render('Select Level:', True, 'white')
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 250))

    # Original Level button - position [WIDTH // 2 - 150, 300, 300, 50]
    pygame.draw.rect(screen, 'blue' if level_source == 'original' else 'white',
                     [WIDTH // 2 - 150, 300, 300, 50], 0 if level_source == 'original' else 2, 10)
    original_text = font.render('Original Level', True, 'white' if level_source == 'original' else 'blue')
    screen.blit(original_text, (WIDTH // 2 - original_text.get_width() // 2, 315))

    # Generated Maze button - position [WIDTH // 2 - 150, 370, 300, 50]
    pygame.draw.rect(screen, 'blue' if level_source == 'generated' else 'white',
                     [WIDTH // 2 - 150, 370, 300, 50], 0 if level_source == 'generated' else 2, 10)
    generated_text = font.render('Generated Maze', True, 'white' if level_source == 'generated' else 'blue')
    screen.blit(generated_text, (WIDTH // 2 - generated_text.get_width() // 2, 385))

    # Ghost movement section
    movement_text = font.render('Ghost Movement:', True, 'white')
    screen.blit(movement_text, (WIDTH // 2 - movement_text.get_width() // 2, 450))

    # Original Behavior button - position [WIDTH // 2 - 150, 500, 300, 50]
    pygame.draw.rect(screen, 'blue' if ghost_movement == 'original' else 'white',
                     [WIDTH // 2 - 150, 500, 300, 50], 0 if ghost_movement == 'original' else 2, 10)
    original_move_text = font.render('Original Behavior', True, 'white' if ghost_movement == 'original' else 'blue')
    screen.blit(original_move_text, (WIDTH // 2 - original_move_text.get_width() // 2, 515))

    # Pathfinding Behavior button - position [WIDTH // 2 - 150, 570, 300, 50]
    pygame.draw.rect(screen, 'blue' if ghost_movement == 'pathfinding' else 'white',
                     [WIDTH // 2 - 150, 570, 300, 50], 0 if ghost_movement == 'pathfinding' else 2, 10)
    pathfinding_text = font.render('Pathfinding Behavior', True,
                                   'white' if ghost_movement == 'pathfinding' else 'blue')
    screen.blit(pathfinding_text, (WIDTH // 2 - pathfinding_text.get_width() // 2, 585))

    # Algorithm selection - only shown if pathfinding is selected
    if ghost_movement == 'pathfinding':
        alg_text = font.render('Pathfinding Algorithm:', True, 'white')
        screen.blit(alg_text, (WIDTH // 2 - alg_text.get_width() // 2, 630))

        # BFS button - position [WIDTH // 2 - 150, 670, 300, 40]
        pygame.draw.rect(screen, 'blue' if path_alg == 'bfs' else 'white',
                         [WIDTH // 2 - 150, 670, 300, 40], 0 if path_alg == 'bfs' else 2, 10)
        bfs_text = font.render('BFS', True, 'white' if path_alg == 'bfs' else 'blue')
        screen.blit(bfs_text, (WIDTH // 2 - bfs_text.get_width() // 2, 680))

        # DFS button - position [WIDTH // 2 - 150, 720, 300, 40]
        pygame.draw.rect(screen, 'blue' if path_alg == 'dfs' else 'white',
                         [WIDTH // 2 - 150, 720, 300, 40], 0 if path_alg == 'dfs' else 2, 10)
        dfs_text = font.render('DFS', True, 'white' if path_alg == 'dfs' else 'blue')
        screen.blit(dfs_text, (WIDTH // 2 - dfs_text.get_width() // 2, 730))

        # Dijkstra button - position [WIDTH // 2 - 150, 770, 300, 40]
        pygame.draw.rect(screen, 'blue' if path_alg == 'dijkstra' else 'white',
                         [WIDTH // 2 - 150, 770, 300, 40], 0 if path_alg == 'dijkstra' else 2, 10)
        dijkstra_text = font.render('Dijkstra', True, 'white' if path_alg == 'dijkstra' else 'blue')
        screen.blit(dijkstra_text, (WIDTH // 2 - dijkstra_text.get_width() // 2, 780))

    # Start button - position [WIDTH // 2 - 100, 850, 200, 60]
    if level_source is not None:
        pygame.draw.rect(screen, 'green', [WIDTH // 2 - 100, 850, 200, 60], 0, 10)
        start_text = font.render('START GAME', True, 'white')
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 870))



def check_ghost_player_collision():
    """Unified ghost collision handling"""
    global lives, game_over, moving, startup_counter, score, eaten_ghost

    # Make collision detection more precise
    player_circle = pygame.Rect(player.center_x - 15, player.center_y - 15, 30, 30)

    # Check collision with ghosts
    ghosts = [blinky, inky, pinky, clyde]
    collision_occurred = False

    for i, ghost in enumerate(ghosts):
        if not ghost or not player_circle.colliderect(ghost.rect):
            continue

        if powerup:
            # Ghost gets eaten when powered up
            if not ghost.is_returning_to_box and not eaten_ghost[i]:
                ghost.is_returning_to_box = True
                eaten_ghost[i] = True
                score += (2 ** eaten_ghost.count(True)) * 100
        elif not ghost.is_returning_to_box:
            # Player gets eaten when not powered up
            collision_occurred = True

    if collision_occurred:
        lives -= 1
        if lives > 0:
            # Reset positions but keep score
            startup_counter = 0
            moving = False
            reset_player_and_ghosts()
        else:
            game_over = True
            moving = False
            startup_counter = 0


def check_pellet_collisions():
    """Check collisions with pellets and update score and powerups"""
    global score, powerup, power_counter, eaten_ghost

    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30

    if 0 < player.center_x < WIDTH:
        # Get the tile position using integer division and explicit int() conversion
        tile_x = int(player.center_x // num2)
        tile_y = int(player.center_y // num1)

        # Ensure we don't try to access out of bounds
        if 0 <= tile_y < len(level) and 0 <= tile_x < len(level[0]):
            current_tile = level[tile_y][tile_x]

            # Check for regular pellet
            if current_tile == 1:
                level[tile_y][tile_x] = 0
                score += 10

            # Check for power pellet - use elif to avoid double processing
            elif current_tile == 2:
                level[tile_y][tile_x] = 0
                score += 50
                powerup = True
                power_counter = 0
                eaten_ghost = [False, False, False, False]

    return score, powerup, power_counter, eaten_ghost


def get_targets():
    """Calculate target positions for each ghost based on game state and player position"""
    # Calculate targets for each ghost based on their specific behaviors
    if blinky and inky and pinky and clyde:
        blink_target = blinky.calculate_target(player.center_x, player.center_y, player.direction)

        # Inky needs Blinky's position for his calculation
        ink_target = inky.calculate_target(player.center_x, player.center_y, player.direction,
                                           blinky.center_x, blinky.center_y)

        pink_target = pinky.calculate_target(player.center_x, player.center_y, player.direction)
        clyd_target = clyde.calculate_target(player.center_x, player.center_y, player.direction)

        return [blink_target, ink_target, pink_target, clyd_target]
    else:
        return [(0, 0)] * 4


def reset_player_and_ghosts():
    """Reset player and ghost positions but keep score"""
    global player, eaten_ghost, powerup, power_counter, moving, startup_counter

    # Reset power state
    powerup = False
    power_counter = 0
    eaten_ghost = [False, False, False, False]

    # Get starting positions
    (start_x, start_y), ghost_starts = get_initial_positions(level_source, level)

    # Reset player
    player.x = start_x
    player.y = start_y
    player.center_x = start_x + 23
    player.center_y = start_y + 24
    player.direction = 0
    player.command = 0

    # Reset ghosts
    for ghost, name in zip([blinky, inky, pinky, clyde], ["blinky", "inky", "pinky", "clyde"]):
        if ghost:
            ghost_x, ghost_y = ghost_starts[name]
            ghost.x_pos = ghost_x
            ghost.y_pos = ghost_y
            ghost.center_x = ghost_x + 22
            ghost.center_y = ghost_y + 22
            ghost.direction = 0 if name == "blinky" else 2
            ghost.is_returning_to_box = False
            ghost.in_box = name != "blinky"  # Blinky starts outside, others inside

    # Reset game state
    moving = False
    startup_counter = 0


def check_win_condition():
    """Check if player has won by eating all pellets"""
    # If no pellets (1) or power pellets (2) remain, player wins
    return not any(1 in row or 2 in row for row in level)


def handle_menu_events(event):
    """Handle events in the menu screen"""
    global level_source, ghost_movement, game_menu, path_alg

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        print(f"Mouse clicked at position: {mouse_pos}")  # Debug print

        # Define button areas exactly as drawn in draw_menu function
        original_level_btn = pygame.Rect(WIDTH // 2 - 150, 300, 300, 50)
        generated_maze_btn = pygame.Rect(WIDTH // 2 - 150, 370, 300, 50)
        original_behavior_btn = pygame.Rect(WIDTH // 2 - 150, 500, 300, 50)
        pathfinding_behavior_btn = pygame.Rect(WIDTH // 2 - 150, 570, 300, 50)
        bfs_btn = pygame.Rect(WIDTH // 2 - 150, 670, 300, 40)
        dfs_btn = pygame.Rect(WIDTH // 2 - 150, 720, 300, 40)
        dijkstra_btn = pygame.Rect(WIDTH // 2 - 150, 770, 300, 40)
        start_game_btn = pygame.Rect(WIDTH // 2 - 100, 850, 200, 60)

        # Check start game button FIRST before all other checks
        if start_game_btn.collidepoint(mouse_pos):
            print("START GAME button clicked!")  # Debug print
            if level_source is not None:  # Only start if a level is selected
                game_menu = False
                initialize_game()
                return  # Exit after starting

        # Now check all other buttons
        elif original_level_btn.collidepoint(mouse_pos):
            level_source = 'original'
            print(f"Selected: Original Level. level_source={level_source}")

        elif generated_maze_btn.collidepoint(mouse_pos):
            level_source = 'generated'
            print(f"Selected: Generated Maze. level_source={level_source}")

        elif original_behavior_btn.collidepoint(mouse_pos):
            ghost_movement = 'original'
            print(f"Selected: Original Behavior. ghost_movement={ghost_movement}")

        elif pathfinding_behavior_btn.collidepoint(mouse_pos):
            ghost_movement = 'pathfinding'
            print(f"Selected: Pathfinding Behavior. ghost_movement={ghost_movement}")

        # Only check algorithm buttons if pathfinding is selected
        elif ghost_movement == 'pathfinding':
            if bfs_btn.collidepoint(mouse_pos):
                path_alg = 'bfs'
                print(f"Selected: BFS. path_alg={path_alg}")

            elif dfs_btn.collidepoint(mouse_pos):
                path_alg = 'dfs'
                print(f"Selected: DFS. path_alg={path_alg}")

            elif dijkstra_btn.collidepoint(mouse_pos):
                path_alg = 'dijkstra'
                print(f"Selected: Dijkstra. path_alg={path_alg}")

        # Print current state after any click
        print(f"Current state: level_source={level_source}, ghost_movement={ghost_movement}, game_menu={game_menu}")



def handle_game_events(event):
    """Handle events in the game screen"""
    global game_over, game_won, game_menu

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
            player.command = 0
        elif event.key == pygame.K_LEFT:
            player.command = 1
        elif event.key == pygame.K_UP:
            player.command = 2
        elif event.key == pygame.K_DOWN:
            player.command = 3
        elif event.key == pygame.K_SPACE and (game_over or game_won):
            game_menu = True  # Return to menu
        elif event.key == pygame.K_ESCAPE:
            game_menu = True  # Return to menu

    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_RIGHT and player.command == 0:
            player.command = player.direction
        elif event.key == pygame.K_LEFT and player.command == 1:
            player.command = player.direction
        elif event.key == pygame.K_UP and player.command == 2:
            player.command = player.direction
        elif event.key == pygame.K_DOWN and player.command == 3:
            player.command = player.direction


def update_animation_counter():
    """Update the animation counter used for flicker effects"""
    global counter, flicker

    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True


def update_powerup_timer():
    """Update the powerup timer and state"""
    global powerup, power_counter, eaten_ghost

    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False] * 4


def handle_startup_sequence():
    """Handle the startup sequence at the beginning of each life"""
    global moving, startup_counter

    if startup_counter < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True


def update_ghost_speeds():
    """Update ghost speeds based on their states"""
    global ghost_speeds

    # Set base speeds based on powerup state
    if powerup:
        ghost_speeds = [0.75, 0.75, 0.75, 0.75]  # Slower when powered up
    else:
        ghost_speeds = [1, 1, 1, 1]

    # Speed up eaten ghosts
    for i in range(4):
        if eaten_ghost[i]:
            ghost_speeds[i] = 2

    # Apply speeds to ghosts
    if blinky: blinky.speed = ghost_speeds[0]
    if inky: inky.speed = ghost_speeds[1]
    if pinky: pinky.speed = ghost_speeds[2]
    if clyde: clyde.speed = ghost_speeds[3]


def draw_game_elements():
    global game_won

    screen.fill('black')

    # Use appropriate draw function
    if level_source == 'original':
        draw_board_original()
    elif level_source == 'generated':
        draw_board_generated()

    game_won = check_win_condition()

    pygame.draw.circle(screen, 'black', (player.center_x, player.center_y), 20, 2)
    player.draw(screen)

    if blinky: blinky.rect = blinky.draw()
    if inky: inky.rect = inky.draw()
    if pinky: pinky.rect = pinky.draw()
    if clyde: clyde.rect = clyde.draw()

    draw_misc()



def process_movement(turns_allowed):
    """Process movement for player and ghosts"""
    global ghost_speeds

    # Get allowed turns for player and move
    updated_turns = player.get_turns(level)
    player.move(updated_turns)

    # Update ghost states and speeds
    update_ghost_speeds()

    # Get targets for ghosts
    targets = get_targets()

    # Move ghosts with their targets
    if blinky: blinky.move(targets[0])
    if inky: inky.move(targets[1])
    if pinky: pinky.move(targets[2])
    if clyde: clyde.move(targets[3])

    # Apply player direction changes based on command
    if player.command == 0 and updated_turns[0]:
        player.direction = 0
    elif player.command == 1 and updated_turns[1]:
        player.direction = 1
    elif player.command == 2 and updated_turns[2]:
        player.direction = 2
    elif player.command == 3 and updated_turns[3]:
        player.direction = 3

    return updated_turns


def process_collisions():
    """Process pellet and ghost collisions"""
    global score, powerup, power_counter, eaten_ghost

    # Check for pellet collisions
    score, powerup, power_counter, eaten_ghost = check_pellet_collisions()

    # Handle ghost-player collisions
    check_ghost_player_collision()


def handle_screen_wraparound():
    """Handle screen wraparound for player"""
    # Screen wraparound for player
    if player.x > 900:
        player.x = -47
    elif player.x < -50:
        player.x = 897


def main():
    """Main game loop - refactored for clarity"""
    global counter, flicker, powerup, power_counter, moving, startup_counter
    global game_won, game_over, score
    global level_source, ghost_movement, game_menu, eaten_ghost

    # Default selection
    level_source = 'original'
    ghost_movement = 'original'
    eaten_ghost = [False, False, False, False]
    turns_allowed = [False, False, False, False]

    # Main game loop
    run = True
    while run:
        timer.tick(fps)

        # Update animation counter (used for pellet flicker)
        update_animation_counter()

        # Handle all events first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif game_menu:
                handle_menu_events(event)
            else:
                handle_game_events(event)

        # Either show menu or game screen
        if game_menu:
            draw_menu()
        else:
            # Update timers
            player.update_counter()
            update_powerup_timer()
            handle_startup_sequence()

            # Draw all game elements
            draw_game_elements()

            # Process movement if game is active
            if moving:
                turns_allowed = process_movement(turns_allowed)

            # Process collisions and boundaries
            process_collisions()
            handle_screen_wraparound()

        # Update display
        pygame.display.flip()

    # Quit pygame
    pygame.quit()


if __name__ == "__main__":
    main()