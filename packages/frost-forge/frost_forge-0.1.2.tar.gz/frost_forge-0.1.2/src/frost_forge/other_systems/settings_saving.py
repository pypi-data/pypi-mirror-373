import os

import pygame as pg


SETTINGS_FILE = os.path.normpath(os.path.join(__file__, "../..", "settings.txt"))

def settings_load():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            controls = [int(i) for i in file.read().split(";")[0].split(":") if i]
    else:
        controls = [pg.K_w, pg.K_a, pg.K_s, pg.K_d, pg.K_e, pg.K_z, pg.K_x, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_0, pg.K_PLUS, pg.K_LSHIFT, pg.K_RIGHT, pg.K_LEFT, pg.K_ESCAPE, pg.K_DOWN, pg.K_UP, pg.K_LCTRL]
    return controls

def settings_save(controls):
    control_str = ""
    for i in controls:
        control_str += f"{i}:"
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        file.write(f"{control_str}")