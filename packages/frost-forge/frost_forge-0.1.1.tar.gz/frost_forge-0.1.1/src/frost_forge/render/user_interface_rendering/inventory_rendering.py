import pygame as pg

from ...info import SCREEN_SIZE, UI_SCALE, UI_FONT, INVENTORY_SIZE, SLOT_SIZE, TILE_UI_SIZE, FLOOR_SIZE, HALF_SCREEN_SIZE, FLOOR

def render_inventory(inventory_number, window, images, inventory):
    for i in range(0, INVENTORY_SIZE[0]):
        if i == inventory_number:
            window.blit(pg.transform.scale(images["inventory_slot_2"], SLOT_SIZE), (HALF_SCREEN_SIZE + (32 * i - 16 * INVENTORY_SIZE[0]) * UI_SCALE, SCREEN_SIZE[1] - 32 * UI_SCALE))
        else:
            window.blit(pg.transform.scale(images["inventory_slot"], SLOT_SIZE), (HALF_SCREEN_SIZE + (32 * i - 16 * INVENTORY_SIZE[0]) * UI_SCALE, SCREEN_SIZE[1] - 32 * UI_SCALE))
    t = 0
    for item in inventory:
        if item not in FLOOR:
            window.blit(pg.transform.scale(images[item], TILE_UI_SIZE), (HALF_SCREEN_SIZE + (32 * t - 16 * INVENTORY_SIZE[0] + 8) * UI_SCALE, SCREEN_SIZE[1] - 28 * UI_SCALE))
        else:
            window.blit(pg.transform.scale(images[item], FLOOR_SIZE), (HALF_SCREEN_SIZE + (32 * t - 16 * INVENTORY_SIZE[0] + 8) * UI_SCALE, SCREEN_SIZE[1] - 20 * UI_SCALE))
        window.blit(UI_FONT.render(str(inventory[item]), False, (19, 17, 18)), (HALF_SCREEN_SIZE + (32 * t - 16 * INVENTORY_SIZE[0] + 4) * UI_SCALE, SCREEN_SIZE[1] - 24 * UI_SCALE))
        t += 1
    return window