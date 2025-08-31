from json import dumps
from os import path

from ...render.menu_rendering import SAVES_FOLDER

def option(state, chunks):
    if state.menu_placement == "options_game":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "main_game"
        elif 100 <= state.position[1] <= 150:
            if state.save_file_name != "" and state.save_file_name.split("_")[0] != "autosave":
                state.menu_placement = "main_menu"
                with open(path.join(SAVES_FOLDER, state.save_file_name + ".txt"), "w", encoding="utf-8") as file:
                    file.write(f"{chunks};{state.location['tile']};{state.tick};{state.noise_offset};{state.world_type}")
                state.save_file_name = ""
                state.machine_ui = "game"
            else:
                state.menu_placement = "save_creation"
    elif state.menu_placement == "options_main":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "main_menu"
    if 200 <= state.position[1] <= 250:
        state.control_adjusted = -1
        state.menu_placement = "controls_options"