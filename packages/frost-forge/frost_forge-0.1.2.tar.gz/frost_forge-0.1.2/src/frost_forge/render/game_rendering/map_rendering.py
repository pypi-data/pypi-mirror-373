from ...info import TILE_SIZE, HALF_SIZE, CHUNK_SIZE, SCREEN_SIZE, MULTI_TILES, ATTRIBUTES
from .border_rendering import render_border


def render_map(location, chunks, camera, zoom, scaled_image, window, images):
    for chunk_y in range(-3, 4):
        for chunk_x in range(-3, 4):
            chunk = (chunk_x + location["tile"][0], chunk_y + location["tile"][1])
            if chunk in chunks:
                for y in range(0, 16):
                    for x in range(0, 16):
                        tile = (x, y)
                        if tile in chunks[chunk]:
                            current_tile = chunks[chunk][tile]
                            placement = (camera[0] + (x * TILE_SIZE + chunk[0] * CHUNK_SIZE) * zoom, camera[1] + (y * TILE_SIZE + chunk[1] * CHUNK_SIZE) * zoom,)
                            if -TILE_SIZE * zoom <= placement[0] <= SCREEN_SIZE[0] and -TILE_SIZE * zoom <= placement[1] <= SCREEN_SIZE[1]:
                                if "floor" in chunks[chunk][tile]:
                                    window.blit(scaled_image[current_tile["floor"]], placement)
                                    render_border(chunk, x, y, chunks, placement, zoom, window, current_tile)
    for chunk_y in range(-3, 4):
        for chunk_x in range(-3, 4):
            chunk = (chunk_x + location["tile"][0], chunk_y + location["tile"][1])
            if chunk in chunks:
                for y in range(0, 16):
                    for x in range(0, 16):
                        tile = (x, y)
                        if tile in chunks[chunk] and "kind" in chunks[chunk][tile] and "point" not in ATTRIBUTES.get(chunks[chunk][tile]["kind"], ()):
                            current_tile = chunks[chunk][tile]
                            placement = (camera[0] + (x * TILE_SIZE + chunk[0] * CHUNK_SIZE) * zoom, camera[1] + (y * TILE_SIZE + chunk[1] * CHUNK_SIZE - HALF_SIZE) * zoom,)
                            size = MULTI_TILES.get(current_tile["kind"], (1, 1))
                            if -TILE_SIZE * zoom * size[0] <= placement[0] <= SCREEN_SIZE[0] and -TILE_SIZE * zoom * size[1] * 3 / 2 <= placement[1] <= SCREEN_SIZE[1]:
                                if isinstance(chunks[chunk][tile]["kind"], str):
                                    window.blit(scaled_image[current_tile["kind"]], placement)
                                if "table" in ATTRIBUTES.get(current_tile["kind"], ()) and "inventory" in current_tile:
                                    window.blit(scaled_image[list(current_tile["inventory"])[0]], (placement[0], placement[1] - HALF_SIZE * zoom * (images[list(current_tile["inventory"])[0]].get_size()[1] // 8 - 2)))
    return window