import pygame
import heapq
from collections import deque

# Constants (reuse your config in future for integration)
WIDTH, HEIGHT = 600, 600
TILE_SIZE = 20
VISUAL_DELAY = 30  # ms

N, S, E, W = 1, 2, 4, 8
IN = 0x10

# Internal utility to draw the maze
def draw_maze(screen, level, path=None, current=None, explored=None, parent=None):
    rows, cols = len(level), len(level[0])
    cell_width = WIDTH // cols
    cell_height = HEIGHT // rows

    BLACK = (0, 0, 0)
    GREY = (60, 60, 60)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    screen.fill(BLACK)
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            color = GREY if cell & IN else BLACK
            rect = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            pygame.draw.rect(screen, color, rect)

            if cell & S == 0:
                pygame.draw.line(screen, GREEN, rect.bottomleft, rect.bottomright, 2)
            if cell & E == 0:
                pygame.draw.line(screen, GREEN, rect.topright, rect.bottomright, 2)

    if explored and parent:
        for node in explored:
            if parent[node] is not None:
                sx, sy = node
                ex, ey = parent[node]
                pygame.draw.line(screen, BLUE,
                                 (sx * cell_width + cell_width // 2, sy * cell_height + cell_height // 2),
                                 (ex * cell_width + cell_width // 2, ey * cell_height + cell_height // 2), 1)

    if path:
        for i in range(1, len(path)):
            sx, sy = path[i-1]
            ex, ey = path[i]
            pygame.draw.line(screen, RED,
                             (sx * cell_width + cell_width // 2, sy * cell_height + cell_height // 2),
                             (ex * cell_width + cell_width // 2, ey * cell_height + cell_height // 2), 3)

    if current:
        cx, cy = current
        pygame.draw.circle(screen, RED,
                           (cx * cell_width + cell_width // 2, cy * cell_height + cell_height // 2), 4)

    pygame.display.flip()

# Shared path reconstruction
def construct_path(parent, end):
    path = []
    step = end
    while step:
        path.append(step)
        step = parent[step]
    return path[::-1]

def bfs_path(level, start, end, visualize=False):
    """Modified BFS that works with the Pac-Man level format"""
    from collections import deque

    # Check for valid inputs
    if not (0 <= start[0] < len(level[0]) and 0 <= start[1] < len(level) and
            0 <= end[0] < len(level[0]) and 0 <= end[1] < len(level)):
        print(f"Invalid start or end position: {start}, {end}")
        return []

    # Check if start or end is in a wall
    if level[start[1]][start[0]] > 2 or level[end[1]][end[0]] > 2:
        print(f"Start or end is in a wall: start={level[start[1]][start[0]]}, end={level[end[1]][end[0]]}")
        return []

    queue = deque([start])
    visited = {start: None}  # Maps positions to their parent

    while queue:
        current = queue.popleft()

        if current == end:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = visited[current]
            return path[::-1]  # Reverse to get start-to-end

        # Try all four directions
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]  # Up, Down, Right, Left
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)

            # Check if valid and not visited
            if (0 <= nx < len(level[0]) and 0 <= ny < len(level) and
                    level[ny][nx] <= 2 and neighbor not in visited):
                queue.append(neighbor)
                visited[neighbor] = current

    print("No path found")
    return []  # No path found


def dfs_path(level, start, end, visualize=False):
    """Modified DFS that works with the Pac-Man level format"""
    # Check for valid inputs
    if not (0 <= start[0] < len(level[0]) and 0 <= start[1] < len(level) and
            0 <= end[0] < len(level[0]) and 0 <= end[1] < len(level)):
        print(f"Invalid start or end position: {start}, {end}")
        return []

    # Check if start or end is in a wall
    if level[start[1]][start[0]] > 2 or level[end[1]][end[0]] > 2:
        print(f"Start or end is in a wall: start={level[start[1]][start[0]]}, end={level[end[1]][end[0]]}")
        return []

    stack = [start]
    visited = {start: None}  # Maps positions to their parent

    while stack:
        current = stack.pop()

        if current == end:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = visited[current]
            return path[::-1]  # Reverse to get start-to-end

        # Try all four directions
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]  # Up, Down, Right, Left
        # Reverse order for DFS to prefer right and down movements
        for dx, dy in reversed(directions):
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)

            # Check if valid and not visited
            if (0 <= nx < len(level[0]) and 0 <= ny < len(level) and
                    level[ny][nx] <= 2 and neighbor not in visited):
                stack.append(neighbor)
                visited[neighbor] = current

    print("No path found")
    return []  # No path found


def dijkstra_path(level, start, end, visualize=False):
    """Modified Dijkstra that works with the Pac-Man level format"""
    import heapq

    # Check for valid inputs
    if not (0 <= start[0] < len(level[0]) and 0 <= start[1] < len(level) and
            0 <= end[0] < len(level[0]) and 0 <= end[1] < len(level)):
        print(f"Invalid start or end position: {start}, {end}")
        return []

    # Check if start or end is in a wall
    if level[start[1]][start[0]] > 2 or level[end[1]][end[0]] > 2:
        print(f"Start or end is in a wall: start={level[start[1]][start[0]]}, end={level[end[1]][end[0]]}")
        return []

    # Priority queue with (cost, position)
    queue = [(0, start)]
    visited = {}  # Maps positions to (cost, parent)
    visited[start] = (0, None)

    while queue:
        cost, current = heapq.heappop(queue)

        # Check if we've already found a better path
        if current in visited and visited[current][0] < cost:
            continue

        if current == end:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = visited[current][1]  # Get parent
            return path[::-1]  # Reverse to get start-to-end

        # Try all four directions
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]  # Up, Down, Right, Left
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)

            # Check if valid
            if (0 <= nx < len(level[0]) and 0 <= ny < len(level) and level[ny][nx] <= 2):
                # We'll use uniform cost for simplicity
                new_cost = cost + 1

                # If we haven't visited this node or found a better path
                if neighbor not in visited or new_cost < visited[neighbor][0]:
                    visited[neighbor] = (new_cost, current)
                    heapq.heappush(queue, (new_cost, neighbor))

    print("No path found")
    return []  # No path found