import pygame as pg

from ...info import FLOOR, STORAGE, SCREEN_SIZE, UI_SCALE, SLOT_SIZE, TILE_UI_SIZE, UI_FONT, FLOOR_SIZE, HALF_SCREEN_SIZE

def render_store(window, machine_ui, images, machine_inventory):
    for item in range(0, STORAGE[machine_ui][0]):
        window.blit(pg.transform.scale(images["inventory_slot"], SLOT_SIZE), (HALF_SCREEN_SIZE + (32 * (item % 7) - 112) * UI_SCALE, SCREEN_SIZE[1] + (32 * (item // 7) - 144) * UI_SCALE))
    t = 0
    for item in machine_inventory:
        position = (HALF_SCREEN_SIZE + (32 * (t % 7) - 104) * UI_SCALE, SCREEN_SIZE[1] + (32 * (t // 7) - 140) * UI_SCALE)
        if item not in FLOOR:
            window.blit(pg.transform.scale(images[item], TILE_UI_SIZE), position)
        else:
            window.blit(pg.transform.scale(images[item], FLOOR_SIZE), (position[0], position[1] + 8 * UI_SCALE))
        window.blit(UI_FONT.render(str(machine_inventory[item]), False, (19, 17, 18)), position)
        t += 1
    return window