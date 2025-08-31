from random import random

from ...info import GROW_CHANCE, GROW_TILES, FPS

def grow(tile, guarantee = False):
    if random() < 1 / (GROW_CHANCE[tile["kind"]] * FPS) or guarantee:
        floor = tile["floor"]
        if "spawn" in tile:
            spawn = tile["spawn"]
            tile = GROW_TILES[tile["kind"]]
            tile["spawn"] = spawn
        else:
            tile = GROW_TILES[tile["kind"]]
        tile["floor"] = floor
    return tile