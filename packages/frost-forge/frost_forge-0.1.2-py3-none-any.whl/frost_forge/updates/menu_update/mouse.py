from .load_save import save_loading
from .create_save import save_creating
from .options import option
from ...info import SCREEN_SIZE, WORLD_TYPES
from ...other_systems.game_saving import save_game


def update_mouse(state, event, chunks):
    if state.menu_placement == "load_save":
        if state.position[1] <= 50:
            state.menu_placement = "main_menu"
        elif state.position[1] <= 100:
            state.menu_placement = "save_options"
            state.world_type = 0
            state.seed = ""
        else:
            chunks = save_loading(state, chunks)
    elif state.menu_placement.startswith("options"):
        option(state, chunks)

    elif state.menu_placement == "save_options":
        if state.position[1] <= 50:
            chunks = save_creating(state, chunks)
        elif state.position[1] <= 100:
            state.world_type = (state.world_type + 1) % len(WORLD_TYPES)
    elif state.menu_placement == "save_creation":
        if 200 <= state.position[1] <= 250 and state.save_file_name != "" and state.save_file_name.split("_")[0] != "autosave":
            state.menu_placement = "main_menu"
            save_game(chunks, state, state.save_file_name)
            state.save_file_name = ""
            chunks = {}
        elif 300 <= state.position[1] <= 350:
            state.menu_placement = "main_menu"
            state.save_file_name = ""
            chunks = {}

    elif state.menu_placement == "main_menu":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "load_save"
        elif 100 <= state.position[1] <= 150:
            state.menu_placement = "options_main"
        elif 200 <= state.position[1] <= 250:
            state.run = False

    elif state.menu_placement == "controls_options":
        if event.button == 4:
            if state.scroll > 0:
                state.scroll -= 1
        elif event.button == 5:
            if state.scroll < len(state.controls) - SCREEN_SIZE[1] // 50 - 1:
                state.scroll += 1
        else:
            state.control_adjusted = state.scroll + state.position[1] // 50
    return chunks