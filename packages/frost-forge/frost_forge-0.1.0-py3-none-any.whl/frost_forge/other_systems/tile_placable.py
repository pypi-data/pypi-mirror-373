from ..info import MULTI_TILES, ATTRIBUTES, FLOOR_TYPE

def is_placable(kind, grid_position, chunks):
    tile_size = MULTI_TILES.get(kind, (1, 1))
    for x in range(0, tile_size[0]):
        for y in range(0, tile_size[1]):
            tile_coord = (int((grid_position[1][0] + x) % 16), int((grid_position[1][1] + y) % 16))
            chunk_coord = (grid_position[0][0] + (grid_position[1][0] + x) // 16, grid_position[0][1] + (grid_position[1][1] + y) // 16)
            if tile_coord in chunks[chunk_coord]:
                current_tile = chunks[chunk_coord][tile_coord]
                tile_floor_type = FLOOR_TYPE.get(current_tile["floor"])
                if tile_floor_type == "block" or tile_floor_type == "fluid" or "grow" in ATTRIBUTES.get(kind, ()) and tile_floor_type != "soil" or "kind" in current_tile:
                    return False
            elif "grow" in ATTRIBUTES.get(kind, ()):
                return False
    return True