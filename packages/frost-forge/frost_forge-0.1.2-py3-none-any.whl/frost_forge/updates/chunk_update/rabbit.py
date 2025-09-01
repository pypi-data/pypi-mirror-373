from random import choice, randint

from .find_empty_place import find_empty_place


def rabbit_hole(chunks, chunk, tile, current_tile, create_tiles):
    if randint(0, 10000) == 0:
        spawn_pos = (chunk[0] * 16 + tile[0], chunk[1] * 16 + tile[1])
        animal = choice(({"kind": "rabbit adult", "inventory": {"rabbit meat": 2, "rabbit fur": 1}, "spawn": spawn_pos}, {"kind": "rabbit child", "spawn": spawn_pos}))
        if animal["kind"] in current_tile["inventory"]:
            empty = find_empty_place(tile, chunk, chunks)
            if empty:
                x, y = empty
                current_tile["inventory"][animal["kind"]] -= 1
                if current_tile["inventory"][animal["kind"]] <= 0:
                    del current_tile["inventory"][animal["kind"]]
                create_tiles.append((
                    (chunk[0] + (tile[0] + x) // 16, chunk[1] + (tile[1] + y) // 16),
                    ((tile[0] + x) % 16, (tile[1] + y) % 16),
                    animal
                ))
    return chunks, create_tiles

def rabbit_entity(chunks, chunk, tile, current_tile, create_tiles, delete_tiles):
    if randint(0, 100) == 0:
        empty = find_empty_place(tile, chunk, chunks)
        if empty:
            x, y = empty
            if abs(chunk[0] * 16 + tile[0] + x - current_tile["spawn"][0]) <= 8 and \
                abs(chunk[1] * 16 + tile[1] + y - current_tile["spawn"][1]) <= 8:
                create_tiles.append((
                    (chunk[0] + (tile[0] + x) // 16, chunk[1] + (tile[1] + y) // 16),
                    ((tile[0] + x) % 16, (tile[1] + y) % 16),
                    {"kind": current_tile["kind"], "inventory": current_tile["inventory"], "spawn": current_tile["spawn"]}
                ))
                delete_tiles.append((chunk, tile))
    return create_tiles, delete_tiles