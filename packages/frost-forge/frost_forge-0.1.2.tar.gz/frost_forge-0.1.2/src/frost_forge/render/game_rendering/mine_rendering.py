import pygame as pg

from ...info import TILE_SIZE, CHUNK_SIZE, HEALTH


def render_mined(location, chunks, camera, zoom, window, images):
    if location[0] in chunks and location[1] in chunks[location[0]]:
        placement = (camera[0] + (location[1][0] * TILE_SIZE + location[0][0] * CHUNK_SIZE) * zoom, camera[1] + (location[1][1] * TILE_SIZE + location[0][1] * CHUNK_SIZE + 60) * zoom,)
        current_tile = chunks[location[0]][location[1]]
        if "health" in current_tile:
            if "kind" in chunks[location[0]][location[1]]:
                max_health = HEALTH[current_tile["kind"]]
            else:
                max_health = HEALTH[current_tile["floor"]]
            window.blit(pg.transform.scale(images["tiny_bar"], (TILE_SIZE * zoom, 16 * zoom)), placement)
            if current_tile["health"] // max_health == 0:
                break_image = images[f"break_{8 - (current_tile["health"] * 8 // max_health)}"]
                break_image.set_alpha(127)
                window.blit(pg.transform.scale(break_image, (TILE_SIZE * zoom, TILE_SIZE * zoom)), (placement[0], placement[1] - TILE_SIZE * zoom))
            pg.draw.rect(window, (181, 102, 60), pg.Rect(placement[0] + 4 * zoom, placement[1] + 4 * zoom, current_tile["health"] * 44 * zoom / max_health, 8 * zoom))
    return window