def create_tile(chunks, create_tiles):
    for chunk_pos, tile_pos, tile_data in create_tiles:
        chunk_tiles = chunks.setdefault(chunk_pos, {})
        if tile_pos in chunk_tiles:
            current_tile = chunk_tiles[tile_pos]
            tile_data["floor"] = current_tile["floor"]
        chunk_tiles[tile_pos] = tile_data
    return chunks

def delete_tile(chunks, delete_tiles):
    for chunk_pos, tile_pos in delete_tiles:
        tile = chunks[chunk_pos][tile_pos]
        if "floor" in tile:
            chunks[chunk_pos][tile_pos] = {"floor": tile["floor"]}
        else:
            del chunks[chunk_pos][tile_pos]
    return chunks