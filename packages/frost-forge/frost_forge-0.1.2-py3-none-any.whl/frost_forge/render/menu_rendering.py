import os

import pygame as pg

from ..info import SCREEN_SIZE, WORLD_TYPES

pg.font.init()


MENU_FONT = pg.font.SysFont("Lucida Console", 50)
CONTROL_NAMES = ["Move up ", "Move left ", "Move down ", "Move right", "Inventory ", "Zoom in", "Zoom out", "Slot 1", "Slot 2", "Slot 3", "Slot 4", "Slot 5", "Slot 6", "Slot 7", "Slot 8", "Slot 9", "Slot 10", "Slot 11", "Slot 12", "Hotbar scroll right", "Hotbar scroll left", "Go to menu", "Menu scroll down", "Menu scroll up", "Sneak"]
SAVES_FOLDER = os.path.normpath(os.path.join(__file__, "../../..", "saves"))

if not os.path.exists(SAVES_FOLDER):
    os.makedirs(SAVES_FOLDER)

def render_menu(
    menu_placement: str,
    save_file_name: str,
    controls: list,
    window,
    scroll,
    control_adjusted,
    world_type,
    seed,
):
    window.fill((206, 229, 242))
    if menu_placement == "load_save":
        window.blit(MENU_FONT.render("Back to menu", False, (19, 17, 18)), (0, 0))
        window.blit(MENU_FONT.render("Create new world", False, (19, 17, 18)), (0, 50))
        saves = [f[:-len(".txt")] for f in os.listdir(SAVES_FOLDER)]
        for i in range(0, len(saves)):
            window.blit(MENU_FONT.render(f"[x] [{saves[i].capitalize()}]", False, (19, 17, 18)), (0, 100 + i * 50))
    elif menu_placement == "save_creation":
        window.blit(MENU_FONT.render("Name your new save?", False, (19, 17, 18)), (0, 0))
        window.blit(MENU_FONT.render(save_file_name.capitalize(), False, (19, 17, 18)), (0, 100))
        window.blit(MENU_FONT.render("Proceed", False, (19, 17, 18)), (0, 200))
        window.blit(MENU_FONT.render("Don't save", False, (19, 17, 18)), (0, 300))
    elif menu_placement == "save_options":
        window.blit(MENU_FONT.render("Create new save", False, (19, 17, 18)), (0, 0))
        window.blit(MENU_FONT.render(f"World type: {WORLD_TYPES[world_type].capitalize()}", False, (19, 17, 18)), (0, 50))
        window.blit(MENU_FONT.render(f"World seed: {seed.capitalize()}", False, (19, 17, 18)), (0, 100))
    elif menu_placement.split("_")[0] == "options":
        if menu_placement == "options_game":
            window.blit(MENU_FONT.render("Return to game", False, (19, 17, 18)), (0, 0))
            window.blit(MENU_FONT.render("Save and Quit", False, (19, 17, 18)), (0, 100))
        elif menu_placement == "options_main":
            window.blit(MENU_FONT.render("Back to menu", False, (19, 17, 18)), (0, 0))
        window.blit(MENU_FONT.render("Controls options", False, (19, 17, 18)), (0, 200))
    elif menu_placement == "main_menu":
        window.blit(MENU_FONT.render("Play", False, (19, 17, 18)), (0, 0))
        window.blit(MENU_FONT.render("Options", False, (19, 17, 18)), (0, 100))
        window.blit(MENU_FONT.render("Quit Game", False, (19, 17, 18)), (0, 200))
    elif menu_placement == "controls_options":
        pg.draw.rect(window, (181, 102, 60), pg.Rect(0, 50 * (control_adjusted - scroll), SCREEN_SIZE[0], 50))
        for y in range(0, len(controls)):
            window.blit(MENU_FONT.render(f"{CONTROL_NAMES[y]}: {pg.key.name(controls[y]).capitalize()}", False, (19, 17, 18)), (0, 50 * (y - scroll)))
    return window