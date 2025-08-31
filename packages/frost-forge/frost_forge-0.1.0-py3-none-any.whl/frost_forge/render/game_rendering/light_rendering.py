from math import cos, pi

import pygame as pg

from ...info import TILE_SIZE, HALF_SIZE, CHUNK_SIZE, SCREEN_SIZE, DAY_LENGTH, ATTRIBUTES

def create_light_surface(intensity: int, color: tuple[int, int, int]):
    light_surface = pg.Surface((32, 32), pg.SRCALPHA)
    for i in range(16, 0, -1):
        alpha = intensity - int((i / 16) * intensity)
        pg.draw.circle(light_surface, (*color, alpha), (16, 16), i)
    return light_surface

LIGHTS = {"campfire": (create_light_surface(170, (181, 102, 60)), 832)}

def render_lights(tick, chunks, location, zoom, camera, window):
    dark_overlay = pg.Surface(SCREEN_SIZE)
    dark_overlay.fill((19, 17, 18))
    dark_overlay.set_alpha(int((1 - cos(((tick / DAY_LENGTH * 2) - 1 / 2) * pi)) * 95))
    window.blit(dark_overlay, (0, 0))

    for x in range(-3, 4):
        for y in range(-3, 4):
            chunk = (x + location["tile"][0], y + location["tile"][1])
            if chunk in chunks:
                for tile in chunks[chunk]:
                    current_tile = chunks[chunk][tile]
                    if "kind" in current_tile and "light" in ATTRIBUTES.get(current_tile["kind"], ()):
                        scaled_glow = pg.transform.scale(LIGHTS[current_tile["kind"]][0], (int(LIGHTS[current_tile["kind"]][1] * zoom), int(LIGHTS[current_tile["kind"]][1] * zoom)))
                        night_factor = 1 - cos(((tick / DAY_LENGTH * 2) - 1 / 2) * pi)
                        scaled_glow.set_alpha(int(night_factor * 180))
                        placement_x = camera[0] + (tile[0] * TILE_SIZE + chunk[0] * CHUNK_SIZE + HALF_SIZE) * zoom - int(LIGHTS[current_tile["kind"]][1] * zoom / 2)
                        placement_y = camera[1] + (tile[1] * TILE_SIZE + chunk[1] * CHUNK_SIZE + HALF_SIZE) * zoom - int(LIGHTS[current_tile["kind"]][1] * zoom / 2)
                        window.blit(scaled_glow, (placement_x, placement_y))
    return window