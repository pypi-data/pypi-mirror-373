from random import choice


def find_empty_place(tile, chunk, chunks):
    empty_places = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            tile_pos = ((tile[0] + x) % 16, (tile[1] + y) % 16)
            chunk_pos = (chunk[0] + (tile[0] + x) // 16, chunk[1] + (tile[1] + y) // 16)
            if tile_pos not in chunks.get(chunk_pos, {}) or "kind" not in chunks[chunk_pos][tile_pos]:
                empty_places.append((x, y))
    return choice(empty_places) if empty_places else None