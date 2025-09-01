import pygame as pg

from ..info import TILE_SIZE, HALF_SIZE, CHUNK_SIZE, SCREEN_SIZE, MULTI_TILES, FLOOR
from .game_rendering import render_ghost, render_mined, render_hand, render_lights, render_map


def render_tiles(
    chunks,
    location,
    zoom,
    target_zoom,
    inventory,
    inventory_number,
    tick,
    camera,
    position,
    window,
    images
):
    window.fill((206, 229, 242))
    player_pixel_position = (location["real"][2] * TILE_SIZE + location["real"][0] * CHUNK_SIZE + HALF_SIZE, location["real"][3] * TILE_SIZE + location["real"][1] * CHUNK_SIZE + HALF_SIZE)
    interpolation = max(min(abs(1 - target_zoom / zoom) * 0.5 + 0.2, 1.0), 0.0)
    camera = ((SCREEN_SIZE[0] * 5 / 8 - player_pixel_position[0] * zoom - position[0] / 4) * interpolation + camera[0] * (1 - interpolation), (SCREEN_SIZE[1] * 5 / 8 - player_pixel_position[1] * zoom - position[1] / 4) * interpolation + camera[1] * (1 - interpolation))
    scaled_image = {}
    for image in images:
        if image in FLOOR:
            scaled_image[image] = pg.transform.scale(images[image], ((TILE_SIZE + 2) * zoom, (TILE_SIZE + 2) * zoom))
        else:
            size = MULTI_TILES.get(image, (1, 1))
            scaled_image[image] = pg.transform.scale(images[image], ((TILE_SIZE * size[0] + 2) * zoom, ((size[1] + 1 / 2) * TILE_SIZE + 2) * zoom))
    window = render_map(location, chunks, camera, zoom, scaled_image, window, images)
    window = render_hand(inventory, inventory_number, camera, location, zoom, window, images)
    window = render_ghost(position, camera, zoom, chunks, location, inventory, inventory_number, scaled_image, window)
    window = render_lights(tick, chunks, location, zoom, camera, window)
    window = render_mined(location["mined"], chunks, camera, zoom, window, images)
    return camera, window