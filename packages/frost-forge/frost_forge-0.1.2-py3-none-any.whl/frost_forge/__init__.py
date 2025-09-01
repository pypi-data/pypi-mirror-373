import os

import pygame as pg

from .info import FPS
from .other_systems.update import update
from .other_systems.settings_saving import settings_save
from .other_systems.rendering import render
from .other_systems.game_state import GameState


def main() -> None:
    pg.init()
    pg.mouse.set_visible(False)

    state = GameState()
    chunks = {}
    window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    SPRITES_FOLDER = os.path.normpath(os.path.join(__file__, "../..", "sprites"))
    IMAGES = {}
    for filename in os.listdir(SPRITES_FOLDER):
        IMAGES[filename.split(".")[0]] = pg.image.load(os.path.join(SPRITES_FOLDER, filename)).convert_alpha()
    while state.run:
        state.position = pg.mouse.get_pos()
        chunks = update(state, chunks)
        state.camera, window = render(state, chunks, window, IMAGES)
        state.clock.tick(FPS)
    pg.quit()
    settings_save(state.controls)