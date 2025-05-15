import pickle
import random
import argparse
import os

# Maze cell directions
N, S, E, W = 1, 2, 4, 8
IN = 0x10
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}

# Tile codes from Pac-Man
TILE_EMPTY = 0
TILE_DOT = 1
TILE_WALL_VERT = 3
TILE_WALL_HORZ = 4
TILE_CORNER_TR = 5
TILE_CORNER_TL = 6
TILE_CORNER_BL = 7
TILE_CORNER_BR = 8

ROWS, COLS = 10, 10  # Base grid for Kruskal (scaled to tile map)

class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def union(self, u, v):
        root_u = self.find(u)
        root_v = self.find(v)
        if root_u != root_v:
            if self.rank[root_u] > self.rank[root_v]:
                self.parent[root_v] = root_u
            elif self.rank[root_u] < self.rank[root_v]:
                self.parent[root_u] = root_v
            else:
                self.parent[root_v] = root_u
                self.rank[root_u] += 1

def generate_kruskal_maze_grid(rows, cols, seed=None):
    if seed is not None:
        random.seed(seed)

    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    dset = DisjointSet(rows * cols)
    walls = [(x, y, S) for y in range(rows) for x in range(cols) if y < rows - 1] + \
            [(x, y, E) for y in range(rows) for x in range(cols) if x < cols - 1]
    random.shuffle(walls)
    return grid, walls, dset

def carve_maze(grid, walls, dset, display=False):
    rows, cols = len(grid), len(grid[0])

    if display:
        import pygame
        pygame.init()
        scale = 3
        cell_size = 20
        cell_width = scale * cell_size
        cell_height = scale * cell_size
        screen = pygame.display.set_mode((cols * cell_width, rows * cell_height))
        pygame.display.set_caption("Kruskal Maze Grid Generation")

        # Colors
        BLACK = (0, 0, 0)
        DARK_GREY = (75, 75, 75)
        GREEN = (0, 255, 0)

    remaining_walls = set(walls)

    while walls:
        x, y, direction = walls.pop()
        nx, ny = x + DX[direction], y + DY[direction]

        if dset.find(y * cols + x) != dset.find(ny * cols + nx):
            dset.union(y * cols + x, ny * cols + nx)
            grid[y][x] |= direction
            grid[ny][nx] |= OPPOSITE[direction]
            grid[y][x] |= IN
            grid[ny][nx] |= IN
            remaining_walls.remove((x, y, direction))

        if display:
            screen.fill(BLACK)

            for j in range(rows):
                for i in range(cols):
                    cell_x, cell_y = i * cell_width, j * cell_height
                    # Draw cell background
                    color = DARK_GREY if grid[j][i] & IN == 0 else BLACK
                    pygame.draw.rect(screen, color, (cell_x, cell_y, cell_width, cell_height))

                    # Draw walls
                    if grid[j][i] & S == 0:
                        pygame.draw.line(screen, GREEN, (cell_x, cell_y + cell_height), (cell_x + cell_width, cell_y + cell_height), 2)
                    if grid[j][i] & E == 0:
                        pygame.draw.line(screen, GREEN, (cell_x + cell_width, cell_y), (cell_x + cell_width, cell_y + cell_height), 2)

            # Draw remaining walls as lines
            for wall in remaining_walls:
                wx, wy, dir = wall
                if dir == S:
                    pygame.draw.line(screen, GREEN,
                                     (wx * cell_width, (wy + 1) * cell_height),
                                     ((wx + 1) * cell_width, (wy + 1) * cell_height), 2)
                elif dir == E:
                    pygame.draw.line(screen, GREEN,
                                     ((wx + 1) * cell_width, wy * cell_height),
                                     ((wx + 1) * cell_width, (wy + 1) * cell_height), 2)

            pygame.display.flip()
            pygame.time.delay(50)

    if display:
        # Save screenshot of Kruskal grid
        os.makedirs("screenshots", exist_ok=True)
        pygame.image.save(screen, "screenshots/kruskal_preview.png")

        # Wait until quit
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()

    return grid


def maze_to_tile_map(maze, scale=3):
    TILE_DOT = 1
    TILE_WALL = 4

    tile_rows = len(maze) * scale
    tile_cols = len(maze[0]) * scale
    tile_map = [[TILE_WALL for _ in range(tile_cols)] for _ in range(tile_rows)]

    for y in range(len(maze)):
        for x in range(len(maze[0])):
            cx = x * scale + 1
            cy = y * scale + 1

            tile_map[cy][cx] = TILE_DOT

            if maze[y][x] & N:
                tile_map[cy - 1][cx] = TILE_DOT
            if maze[y][x] & S:
                tile_map[cy + 1][cx] = TILE_DOT
            if maze[y][x] & E:
                tile_map[cy][cx + 1] = TILE_DOT
            if maze[y][x] & W:
                tile_map[cy][cx - 1] = TILE_DOT

    return tile_map


def generate_and_save_tile_map(filename="maze_maker/kruskal_tile_map.pkl", display=None, seed=None):
    grid, walls, dset = generate_kruskal_maze_grid(ROWS, COLS, seed)
    maze = carve_maze(grid, walls, dset, display == "kruskal")
    tile_map = maze_to_tile_map(maze)

    if display == "tile":
        import pygame
        pygame.init()
        scale = 3
        cell_size = 20
        width = COLS * scale * cell_size
        height = ROWS * scale * cell_size
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pac-Man Tile Map Visualization")

        color_dict = {
            TILE_DOT: (0, 0, 0),
            TILE_WALL_VERT: (0, 255, 0),
            TILE_WALL_HORZ: (0, 255, 0),
            TILE_CORNER_TR: (0, 255, 0),
            TILE_CORNER_TL: (0, 255, 0),
            TILE_CORNER_BL: (0, 255, 0),
            TILE_CORNER_BR: (0, 255, 0),
            TILE_EMPTY: (30, 30, 30)
        }

        screen.fill((0, 0, 0))

        for y in range(len(tile_map)):
            for x in range(len(tile_map[0])):
                tile_type = tile_map[y][x]
                color = color_dict.get(tile_type, (50, 50, 50))
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, color, rect)

                if tile_type == TILE_DOT:
                    center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
                    pygame.draw.circle(screen, (255, 255, 255), center, cell_size // 6)

                pygame.display.update(rect)
                pygame.time.delay(10)
                os.makedirs("screenshots", exist_ok=True)
                pygame.image.save(screen, "screenshots/tile_preview.png")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        pygame.quit()

    with open(filename, "wb") as f:
        pickle.dump(tile_map, f)
    print(f"Tile-based maze saved to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and optionally display a Kruskal-based Pac-Man maze")
    parser.add_argument("--mode", choices=["tile", "kruskal", "none"], default="none",
                        help="Display mode: 'tile' for Pac-Man tile map, 'kruskal' for raw grid carving, or 'none'")
    parser.add_argument("--seed", type=int, default=None,
                        help="Optional random seed for reproducible maze generation")

    args = parser.parse_args()
    generate_and_save_tile_map(
        display=(args.mode if args.mode != "none" else None),
        seed=args.seed
    )
