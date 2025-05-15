import pickle

# Wall bitmasks
N, S, E, W = 1, 2, 4, 8
IN = 0x10

def convert_kruskal_to_board(pkl_file_path, target_rows=32, target_cols=30):
    with open(pkl_file_path, 'rb') as f:
        maze = pickle.load(f)

    scale_y = target_rows // len(maze)
    scale_x = target_cols // len(maze[0])

    board = [[4 for _ in range(target_cols)] for _ in range(target_rows)]

    for y in range(len(maze)):
        for x in range(len(maze[0])):
            cx = x * scale_x + 1
            cy = y * scale_y + 1

            board[cy][cx] = 1  # center

            if maze[y][x] & N:
                board[cy - 1][cx] = 1
            if maze[y][x] & S:
                board[cy + 1][cx] = 1
            if maze[y][x] & E:
                board[cy][cx + 1] = 1
            if maze[y][x] & W:
                board[cy][cx - 1] = 1

    return board
