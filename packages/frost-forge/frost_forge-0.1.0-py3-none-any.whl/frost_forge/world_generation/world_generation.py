from noise import pnoise2
from random import uniform

from ..info import MULTI_TILES, NOISE_TILES, ATTRIBUTE_CARE, ATTRIBUTES
from .biome_determination import determine_biome

def generate_chunk(
    world_type: int,
    chunk_x: int,
    chunk_y: int,
    chunks: dict[tuple[int, int], dict[tuple[int, int], tuple[dict, dict]]],
    noise_offset: tuple[float, float] = None
):
    if noise_offset == None:
        noise_offset = (uniform(-10000, 10000), uniform(-10000, 10000))
    if (chunk_x, chunk_y) not in chunks:
        chunks[chunk_x, chunk_y] = {}
        tile = chunks[chunk_x, chunk_y]
        if world_type == 0:
            for tile_x in range(0, 16):
                for tile_y in range(0, 16):
                    tile_pos = (tile_x, tile_y)
                    if tile_pos not in tile:
                        world_x = chunk_x * 16 + tile_x + noise_offset[0]
                        world_y = chunk_y * 16 + tile_y + noise_offset[1]
                        biome = determine_biome(world_x, world_y, noise_offset)
                        elevation_value = pnoise2(world_x / 10 + noise_offset[0], world_y / 10 + noise_offset[1], 3, 0.5, 2)
                        moisture_value = pnoise2(world_x / 30 + noise_offset[0], world_y / 30 + noise_offset[1], 3, 0.5, 2)
                        for noise_tile in NOISE_TILES[biome]:
                            if noise_tile[0][0] < elevation_value < noise_tile[0][1] and noise_tile[1][0] < moisture_value < noise_tile[1][1]:
                                tile[tile_pos] = noise_tile[2]
                                break
                        if tile_pos in tile:
                            tile_size = MULTI_TILES.get(tile[tile_pos].get("kind", None), (1, 1))
                            new_tile_x = tile_x - tile_size[0] + 1
                            new_tile_y = tile_y - tile_size[1] + 1
                            can_place = True
                            if tile_x - tile_size[0] + 1 < 0 or tile_y - tile_size[1] + 1 < 0:
                                can_place = False
                            for x in range(0, tile_size[0]):
                                for y in range(0, tile_size[1]):
                                    test_tile = (new_tile_x + x, new_tile_y + y)
                                    if test_tile in tile:
                                        if len(tuple(ATTRIBUTE_CARE & ATTRIBUTES.get(tile[test_tile].get("kind", None), set()))) or "structure" in tile[test_tile]:
                                            can_place = False
                            if can_place:
                                tile[new_tile_x, new_tile_y] = tile[tile_pos]
                                for x in range(0, tile_size[0]):
                                    if x != 0:
                                        tile[new_tile_x + x, new_tile_y] = {"kind": "left"}
                                    for y in range(1, tile_size[1]):
                                        tile[new_tile_x + x, new_tile_y + y] = {"kind": "up"}
                            else:
                                del tile[tile_pos]
    return noise_offset