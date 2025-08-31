import pygame as pg

from ...info import TILE_SIZE, HALF_SIZE, CHUNK_SIZE

def render_hand(inventory, inventory_number, camera, location, zoom, window, images):
    if len(inventory) > inventory_number:
        placement = (camera[0] + (location["tile"][2] * TILE_SIZE + location["tile"][0] * CHUNK_SIZE - 4) * zoom, camera[1] + (location["tile"][3] * TILE_SIZE + location["tile"][1] * CHUNK_SIZE - 8) * zoom)
        hand_image = pg.transform.scale(images[list(inventory.keys())[inventory_number]], (HALF_SIZE * zoom, 3 * TILE_SIZE // 4 * zoom))
        window.blit(hand_image, placement)
    return window