from ..info import ATTRIBUTES, MULTI_TILES

def place_tile(kind, grid_position, chunks):
    if "multi" in ATTRIBUTES.get(kind, ()):
        width, height = MULTI_TILES[kind]
        for x in range(width):
            for y in range(height):
                chunk_pos = (grid_position[0][0] + (grid_position[1][0] + x) // 16, grid_position[0][1] + (grid_position[1][1] + y) // 16)
                tile_pos = ((grid_position[1][0] + x) % 16, (grid_position[1][1] + y) % 16)
                tile_type = "left" if y == 0 else "up"
                old_tile = chunks[chunk_pos].get(tile_pos)
                if old_tile:
                    chunks[chunk_pos][tile_pos] = {"kind": tile_type, "floor": old_tile["floor"]}
                else:
                    chunks[chunk_pos][tile_pos] = {"kind": tile_type}
    if grid_position[1] not in chunks[grid_position[0]]:
        chunks[grid_position[0]][grid_position[1]] = {"kind": kind}
    else:
        old_tile = chunks[grid_position[0]][grid_position[1]]
        chunks[grid_position[0]][grid_position[1]] = {"kind": kind, "floor": old_tile["floor"]}
    return chunks