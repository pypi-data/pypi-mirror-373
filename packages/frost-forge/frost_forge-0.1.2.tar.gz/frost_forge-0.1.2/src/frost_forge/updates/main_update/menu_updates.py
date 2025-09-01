import pygame as pg

from ..menu_update import update_keys, update_mouse


def update_menu(state, chunks):
    for event in pg.event.get():
        if event.type == pg.QUIT:
            state.run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            chunks = update_mouse(state, event, chunks)
        elif event.type == pg.KEYDOWN:
            state.save_file_name, state.controls, state.menu_placement, state.scroll, state.control_adjusted, state.seed = update_keys(state.menu_placement, state.save_file_name, state.controls, state.control_adjusted, chunks, state.scroll, state.seed)
    return chunks