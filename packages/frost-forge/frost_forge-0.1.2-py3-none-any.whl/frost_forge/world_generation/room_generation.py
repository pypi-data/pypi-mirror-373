import os
from PIL import Image, ImageOps
from random import randint

from ..info import ROOM_COLORS
from .loot_calculation import calculate_loot


def generate_room(structure, room, tile_offset, chunk_offset, rotate = True, vary = True):
    room_image = Image.open(os.path.normpath(os.path.join(__file__, "../../..", f"structures/{structure}/{room}.png"))).convert("RGB")
    room_chunks = {}
    if vary:
        variation = randint(0, 15)
        if variation % 2:
            room_image = ImageOps.mirror(room_image)
        if (variation // 2) % 2:
            room_image = ImageOps.flip(room_image)
        if rotate:
            room_image = room_image.rotate((variation // 4) * 90)
    for x in range(0, room_image.size[0]):
        for y in range(0, room_image.size[1]):
            if room_image.getpixel((x, y)) in ROOM_COLORS:
                tile_placement = (x + tile_offset[0]) % 16, (y + tile_offset[1]) % 16
                chunk_placement = (x + tile_offset[0]) // 16 + chunk_offset[0], (y + tile_offset[1]) // 16 + chunk_offset[1]
                if chunk_placement not in room_chunks:
                    room_chunks[chunk_placement] = {}
                room_chunks[chunk_placement][tile_placement] = {}
                tile = ROOM_COLORS[room_image.getpixel((x, y))]
                for index in tile:
                    room_chunks[chunk_placement][tile_placement][index] = tile[index]
                if "loot" in room_chunks[chunk_placement][tile_placement]:
                    room_chunks[chunk_placement][tile_placement] = calculate_loot(room_chunks[chunk_placement][tile_placement])
    return room_chunks