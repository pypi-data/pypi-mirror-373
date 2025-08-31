import pygame as pg

from ..render import render_menu, render_tiles, render_ui
from .game_state import GameState


def render(state: GameState, chunks, window, images) -> tuple:
    if state.menu_placement != "main_game":
        window = render_menu(state.menu_placement, state.save_file_name, state.controls, window, state.scroll, state.control_adjusted, state.world_type)
        window.blit(pg.transform.scale(images["cursor"], (32, 32)), (state.position[0] - 16, state.position[1] - 16))
    else:
        state.camera, window = render_tiles(
            chunks,
            state.location,
            state.zoom,
            state.target_zoom,
            state.inventory,
            state.inventory_number,
            state.tick,
            state.camera,
            state.position,
            window,
            images
        )
        window = render_ui(
            state.inventory_number,
            state.inventory,
            state.machine_ui,
            chunks[state.location["opened"][0]].get(state.location["opened"][1], chunks[0, 0][0, 0]).get("recipe", 0),
            state.health,
            state.machine_inventory,
            window,
            images,
        )
        cursor_size = (int(32 * state.zoom), int(32 * state.zoom))
        cursor_place = (state.position[0] - 16 * state.zoom, state.position[1] - 16 * state.zoom)
        window.blit(pg.transform.scale(images["cursor"], cursor_size), cursor_place)
    pg.display.update()
    return state.camera, window