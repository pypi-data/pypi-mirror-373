import pygame as pg

from ...info import SCREEN_SIZE

def update_keys(menu_placement, save_file_name, controls, control_adjusted, chunks, scroll):
    keys = pg.key.get_pressed()
    if menu_placement == "save_creation":
        for letter in range(48, 123):
            if keys[letter]:
                save_file_name += chr(letter)
        if keys[pg.K_SPACE]:
            save_file_name += " "
        elif keys[pg.K_BACKSPACE]:
            save_file_name = save_file_name[:-1]

    elif menu_placement == "controls_options":
        if control_adjusted > -1:
            for key_code in range(len(keys)):
                if keys[key_code]:
                    controls[control_adjusted] = key_code
                    control_adjusted = -1
        else:
            if keys[controls[21]]:
                menu_placement = "options_game" if chunks != {} else "options_main"
            elif keys[controls[22]]:
                if scroll < len(controls) - SCREEN_SIZE[1] // 50 - 1:
                    scroll += 1
            elif keys[controls[23]]:
                if scroll > 0:
                    scroll -= 1
    return save_file_name, controls, menu_placement, scroll, control_adjusted