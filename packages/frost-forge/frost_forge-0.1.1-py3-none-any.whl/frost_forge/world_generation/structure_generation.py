from random import random

from ..info import NOISE_STRUCTURES, STRUCTURE_ENTRANCE
from .room_generation import generate_room
from .structure_structuring import structure_rooms
from .biome_determination import determine_biome


def generate_structure(noise_offset, chunk_x, chunk_y, chunks, checked):
    if (chunk_x, chunk_y) not in checked:
        checked.add((chunk_x, chunk_y))
        structure_value = random()
        structure = False
        biome = determine_biome(16 * chunk_x, 16 * chunk_y, noise_offset)
        for noise_structure in NOISE_STRUCTURES.get(biome, ()):
            if noise_structure[0][0] < structure_value < noise_structure[0][1]:
                structure_type = noise_structure[1]
                structure = True
                break
        if structure:
            dungeon = structure_rooms(structure_type, (chunk_x, chunk_y))
            for dungeon_room in dungeon[0]:
                chunks[dungeon_room] = {}
                room = generate_room(structure_type, dungeon[0][dungeon_room], (1, 1), (chunk_x, chunk_y), dungeon[0][dungeon_room][0] == dungeon[0][dungeon_room][1])
                for chunk in room:
                    chunks[chunk] = room[chunk]
            if dungeon[2] not in chunks:
                chunks[dungeon[2]] = {}
            chunks[dungeon[2]][7, 1] = STRUCTURE_ENTRANCE[structure_type]
    return chunks, checked