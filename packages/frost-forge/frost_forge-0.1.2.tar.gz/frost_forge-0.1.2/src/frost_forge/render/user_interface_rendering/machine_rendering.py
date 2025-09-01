import pygame as pg

from ...info import FLOOR, SCREEN_SIZE, UI_SCALE, SLOT_SIZE, TILE_UI_SIZE, UI_FONT, FLOOR_SIZE, HALF_SCREEN_SIZE, RECIPES


def render_machine(window, machine_ui, images, machine_inventory, recipe_number):
    machine_recipe = RECIPES[machine_ui][recipe_number]
    for item in range(0, len(machine_recipe[1])):
        window.blit(pg.transform.scale(images["inventory_slot"], SLOT_SIZE), (HALF_SCREEN_SIZE + (32 * (item % 7) - 112) * UI_SCALE, SCREEN_SIZE[1] + (32 * (item // 7) - 144) * UI_SCALE))
    window.blit(pg.transform.scale(images["inventory_slot_2"], SLOT_SIZE), (HALF_SCREEN_SIZE - 112 * UI_SCALE, SCREEN_SIZE[1]- 80 * UI_SCALE))
    for i in range(0, len(machine_recipe[1])):
        position = (HALF_SCREEN_SIZE + (32 * (i % 7) - 104) * UI_SCALE, SCREEN_SIZE[1] + (32 * (i // 7) - 140) * UI_SCALE)
        item = machine_recipe[1][i][0]
        if item not in FLOOR:
            window.blit(pg.transform.scale(images[item], TILE_UI_SIZE), position)
        else:
            window.blit(pg.transform.scale(images[item], FLOOR_SIZE), (position[0], position[1] + 8 * UI_SCALE))
        window.blit(UI_FONT.render(f"{machine_inventory.get(item, 0)}/{machine_recipe[1][i][1]}", False, (19, 17, 18)), (position[0] - 4 * UI_SCALE, position[1]))
    position = (HALF_SCREEN_SIZE - 104 * UI_SCALE, SCREEN_SIZE[1] - 76 * UI_SCALE)
    item = machine_recipe[0][0]
    if item not in FLOOR:
        window.blit(pg.transform.scale(images[item], TILE_UI_SIZE), position)
    else:
        window.blit(pg.transform.scale(images[item], FLOOR_SIZE), (position[0], position[1] + 8 * UI_SCALE))
    window.blit(UI_FONT.render(f"{machine_inventory.get(item, 0)}/{machine_recipe[0][1]}", False, (19, 17, 18)), (position[0] - 4 * UI_SCALE, position[1]))
    return window