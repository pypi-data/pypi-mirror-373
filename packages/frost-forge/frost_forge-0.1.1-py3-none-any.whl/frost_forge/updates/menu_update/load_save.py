from ast import literal_eval
from os import listdir, path, remove

from ...render.menu_rendering import SAVES_FOLDER

def save_loading(state, chunks):
    saves = [f[:-4] for f in listdir(SAVES_FOLDER) if f.endswith(".txt")]
    index = (state.position[1] // 50) - 2
    if index < len(saves):
        state.save_file_name = saves[index]
        if state.position[0] >= 120:
            state.menu_placement = "main_game"
            with open(path.join(SAVES_FOLDER, state.save_file_name + ".txt"), "r", encoding="utf-8") as file:
                file_content = file.read().split(";")
            chunks = literal_eval(file_content[0])
            state.location["tile"] = literal_eval(file_content[1])
            state.tick = int(float(file_content[2]))
            state.location["real"] = list(state.location["tile"])
            state.noise_offset = literal_eval(file_content[3])
            state.world_type = int(file_content[4])
        elif state.position[0] <= 90:
            file_path = path.join(SAVES_FOLDER, state.save_file_name + ".txt")
            if path.exists(file_path):
                remove(file_path)
    return chunks