from random import random

from ...info import FERTILIZER_SPAWN, FERTILIZER_EFFICIENCY, GROW_CHANCE
from ...other_systems.tile_placement import place_tile
from ..chunk_update.growth import grow


def fertilize_spawn(chunks, inventory, inventory_number, grid_position):
    inventory_key = list(inventory.keys())[inventory_number]
    inventory[inventory_key] -= 1
    if inventory[inventory_key] == 0:
        del inventory[inventory_key]
    spawn_number = random()
    spawn = None
    for i in FERTILIZER_SPAWN:
        if spawn_number < i[0] * FERTILIZER_EFFICIENCY[inventory_key]:
            spawn = i[1]
            break
    if isinstance(spawn, str):
        chunks = place_tile(spawn, grid_position, chunks)
    return chunks

def fertilize_grow(chunks, inventory, inventory_number, grid_position):
    inventory_key = list(inventory.keys())[inventory_number]
    current_tile = chunks[grid_position[0]][grid_position[1]]
    if random() < FERTILIZER_EFFICIENCY[inventory_key] / GROW_CHANCE[current_tile["kind"]]:
        chunks[grid_position[0]][grid_position[1]] = grow(current_tile, True)
    inventory[inventory_key] -= 1
    if inventory[inventory_key] == 0:
        del inventory[inventory_key]
    return chunks