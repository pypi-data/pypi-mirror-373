import pygame as pg

from ...info import UI_SCALE, SCREEN_SIZE, BIG_UI_FONT, UI_FONT, SLOT_SIZE, TILE_UI_SIZE, FLOOR_SIZE, HALF_SCREEN_SIZE, RECIPES, FLOOR

def render_craft(window, machine_ui, images, recipe_number):
    current_recipes = RECIPES[machine_ui]
    window.blit(pg.transform.scale(images["big_inventory_slot_2"], (96 * UI_SCALE, 96 * UI_SCALE)), (HALF_SCREEN_SIZE - 128 * UI_SCALE, SCREEN_SIZE[1] - 144 * UI_SCALE))
    if current_recipes[recipe_number][0][0] not in FLOOR:
        window.blit(pg.transform.scale(images[current_recipes[recipe_number][0][0]], (48 * UI_SCALE, 72 * UI_SCALE)), (HALF_SCREEN_SIZE - 104 * UI_SCALE, SCREEN_SIZE[1] - 132 * UI_SCALE))
    else:
        window.blit(pg.transform.scale(images[current_recipes[recipe_number][0][0]], (48 * UI_SCALE, 48 * UI_SCALE)), (HALF_SCREEN_SIZE - 104 * UI_SCALE, SCREEN_SIZE[1] - 108 * UI_SCALE))
    window.blit(BIG_UI_FONT.render(str(current_recipes[recipe_number][0][1]), False, (19, 17, 18)), (HALF_SCREEN_SIZE - 112 * UI_SCALE, SCREEN_SIZE[1] - 80 * UI_SCALE),)
    for inputs in range(0, len(current_recipes[recipe_number][1])):
        position = (HALF_SCREEN_SIZE + ((40 * (inputs % 4) - 32)) * UI_SCALE, SCREEN_SIZE[1] + (32 * (inputs // 4) - 144) * UI_SCALE)
        window.blit(pg.transform.scale(images["inventory_slot"], SLOT_SIZE), position)
        if current_recipes[recipe_number][1][inputs][0] not in FLOOR:
            window.blit(pg.transform.scale(images[current_recipes[recipe_number][1][inputs][0]], TILE_UI_SIZE), (position[0] + 8 * UI_SCALE, position[1] + 4 * UI_SCALE),)
        else:
            window.blit(pg.transform.scale(images[current_recipes[recipe_number][1][inputs][0]], FLOOR_SIZE), (position[0] + 8 * UI_SCALE, position[1] + 12 * UI_SCALE),)
        window.blit(UI_FONT.render(str(current_recipes[recipe_number][1][inputs][1]), False, (19, 17, 18)), (position[0] + 8 * UI_SCALE, position[1] + 32 * UI_SCALE))
    return window