from ...other_systems.game_saving import save_game


def option(state, chunks):
    if state.menu_placement == "options_game":
        if 0 <= state.position[1] <= 50:
            state.menu_placement = "main_game"
        elif 100 <= state.position[1] <= 150:
            if state.save_file_name != "" and state.save_file_name.split("_")[0] != "autosave":
                state.menu_placement = "main_menu"
                save_game(chunks, state, state.save_file_name)
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