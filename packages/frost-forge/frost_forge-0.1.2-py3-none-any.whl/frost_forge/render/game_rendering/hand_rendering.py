import pygame as pg

from ...info import TILE_SIZE, HALF_SIZE, CHUNK_SIZE, FLOOR, MULTI_TILES


def render_hand(inventory, inventory_number, camera, location, zoom, window, images):
    if len(inventory) > inventory_number:
        placement = (camera[0] + (location["tile"][2] * TILE_SIZE + location["tile"][0] * CHUNK_SIZE - 4) * zoom, camera[1] + (location["tile"][3] * TILE_SIZE + location["tile"][1] * CHUNK_SIZE - 8) * zoom)
        inventory_key = list(inventory.keys())[inventory_number]
        hand_size = (1, 3 / 2)
        if inventory_key in FLOOR:
            hand_size = (1, 1)
        elif inventory_key in MULTI_TILES:
            hand_size = (MULTI_TILES[inventory_key][0], MULTI_TILES[inventory_key][1] + 1 / 2)
        hand_image = pg.transform.scale(images[list(inventory.keys())[inventory_number]], (HALF_SIZE * zoom * hand_size[0], HALF_SIZE * zoom * hand_size[1]))
        window.blit(hand_image, placement)
    return window