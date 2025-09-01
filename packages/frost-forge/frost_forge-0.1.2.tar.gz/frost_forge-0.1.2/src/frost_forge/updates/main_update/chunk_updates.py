from ...other_systems.game_state import GameState
from ..chunk_update import update_tile, create_tile, delete_tile


def update_tiles(state: GameState, chunks):
    delete_tiles = []
    create_tiles = []
    tile_location = state.location["tile"]

    for chunk_dx in range(-3, 4):
        for chunk_dy in range(-3, 4):
            chunk = (chunk_dx + tile_location[0], chunk_dy + tile_location[1])
            if chunk in chunks:
                for tile in list(chunks[chunk]):
                    current_tile = chunks[chunk][tile]
                    if "kind" in current_tile:
                        chunks, create_tiles, delete_tiles = update_tile(current_tile, chunks, chunk, tile, delete_tiles, create_tiles, state.tick)

    chunks = create_tile(chunks, create_tiles)
    chunks = delete_tile(chunks, delete_tiles)
    return chunks