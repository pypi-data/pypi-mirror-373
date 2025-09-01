import pygame as pg

from ...info import ATTRIBUTES, SCREEN_SIZE, UI_SCALE, SLOT_SIZE, TILE_UI_SIZE, HALF_SCREEN_SIZE
from .craft_rendering import render_craft
from .store_rendering import render_store
from .machine_rendering import render_machine


def render_open(machine_ui, window, images, recipe_number, machine_inventory):
    attributes = ATTRIBUTES.get(machine_ui, ())
    if "open" in attributes:
        window.blit(pg.transform.scale(images["big_inventory_slot"], (320 * UI_SCALE, 128 * UI_SCALE)), (HALF_SCREEN_SIZE - 160 * UI_SCALE, SCREEN_SIZE[1] - 160 * UI_SCALE))
        window.blit(pg.transform.scale(images["inventory_slot_3"], SLOT_SIZE), (HALF_SCREEN_SIZE + 88 * UI_SCALE, SCREEN_SIZE[1] - 80 * UI_SCALE))
        window.blit(pg.transform.scale(images[machine_ui], TILE_UI_SIZE), (HALF_SCREEN_SIZE + 96 * UI_SCALE, SCREEN_SIZE[1] - 76 * UI_SCALE))
        if "craft" in attributes:
            window = render_craft(window, machine_ui, images, recipe_number)
        elif "machine" in attributes:
            window = render_machine(window, machine_ui, images, machine_inventory, recipe_number)
        elif "store" in attributes:
            window = render_store(window, machine_ui, images, machine_inventory)
    return window