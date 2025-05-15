import copy
import pickle
from board import boards
from maze_maker.kruskal_algorithm import generate_and_save_tile_map

def load_level():
    choice = input("Choose level:\n1 - Original\n2 - Generated Kruskal\n> ").strip()
    if choice == '2':
        level_source = 'generated'
        generate_and_save_tile_map("maze_maker/kruskal_tile_map.pkl")
        with open("maze_maker/kruskal_tile_map.pkl", "rb") as f:
            level = pickle.load(f)
    else:
        level_source = 'original'
        level = copy.deepcopy(boards)
    return level_source, level
