import pygame as pg

from .player_move import move_player
from ...world_generation.world_generation import generate_chunk
from ...world_generation.structure_generation import generate_structure
from ...other_systems.game_state import GameState
from .mouse_update import button_press
from os import path
from ...info import DAY_LENGTH, INVENTORY_SIZE, FLOOR_TYPE, HEALTH
from ...render.menu_rendering import SAVES_FOLDER

def update_game(state: GameState, chunks):
    state.health = chunks[state.location["tile"][0], state.location["tile"][1]][state.location["tile"][2], state.location["tile"][3]].get("health", 20)
    state.location["old"] = list(state.location["tile"])
    state.inventory = chunks[state.location["tile"][0], state.location["tile"][1]][state.location["tile"][2], state.location["tile"][3]].get("inventory", {})
    key = pg.key.get_pressed()
    state.location, state.velocity = move_player(key, state.controls, state.velocity, state.location)

    for x in range(-4, 5):
        for y in range(-4, 5):
            generate_chunk(state.world_type, state.location["tile"][0] + x, state.location["tile"][1] + y, chunks, state.noise_offset)
    if state.world_type == 0:
        for x in range(-20, 20):
            for y in range(-20, 20):
                generate_structure(state.noise_offset, state.location["tile"][0] + x, state.location["tile"][1] + y, chunks, state.checked)

    tile_chunk_coords = (state.location["tile"][0], state.location["tile"][1])
    tile_coords = (state.location["tile"][2], state.location["tile"][3])
    old_chunk_coords = (state.location["old"][0], state.location["old"][1])
    old_tile_coords = (state.location["old"][2], state.location["old"][3])

    chunk = chunks[tile_chunk_coords]
    old_chunk = chunks[old_chunk_coords]
    old_tile = old_chunk[old_tile_coords]

    if tile_coords not in chunk:
        chunk[tile_coords] = {"kind": "player", "inventory": state.inventory, "health": state.health}
    elif "kind" not in chunk[tile_coords] and "door" != FLOOR_TYPE.get(chunk[tile_coords]["floor"]) != "fluid":
        exist_tile = chunk[tile_coords]
        chunk[tile_coords] = {"kind": "player", "inventory": state.inventory, "health": state.health, "floor": exist_tile["floor"]}
    elif chunk[tile_coords].get("kind") != "player":
        state.location["real"] = list(state.location["old"])
        state.location["tile"] = list(state.location["old"])
        state.velocity = [0, 0]

    if state.location["old"] != state.location["tile"]:
        if "floor" in old_tile:
            old_chunk[old_tile_coords] = {"floor": old_tile["floor"], "health": HEALTH.get(old_tile["floor"], 1)}
        else:
            del old_chunk[old_tile_coords]

    for event in pg.event.get():
        if event.type == pg.QUIT:
            state.run = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            chunks, state.location, state.machine_ui, state.machine_inventory, state.tick, state.inventory_number = button_press(
                event.button, state.position, state.zoom, chunks, state.location, state.machine_ui, state.inventory, state.health,
                state.machine_inventory, state.tick, state.inventory_number, chunks[state.location["opened"][0]][state.location["opened"][1]].get("recipe", 0), state.camera)
        elif event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()
            if keys[state.controls[4]]:
                if state.machine_ui == "game":
                    state.machine_ui = "player"
                    state.location["opened"] = ((state.location["tile"][0], state.location["tile"][1]), (state.location["tile"][2], state.location["tile"][3]))
                else:
                    state.machine_ui = "game"
                    state.location["opened"] = ((0, 0), (0, 0))
            elif keys[state.controls[5]] or keys[state.controls[6]]:
                state.target_zoom += (keys[state.controls[5]] - keys[state.controls[6]]) / 4
                state.target_zoom = min(max(state.target_zoom, 0.5), 2)
            elif keys[state.controls[21]]:
                state.menu_placement = "options_game"
            elif keys[state.controls[0]] or keys[state.controls[1]] or keys[state.controls[2]] or keys[state.controls[3]]:
                state.machine_ui = "game"
                state.location["opened"] = ((0, 0), (0, 0))
            elif keys[state.controls[19]]:
                state.inventory_number = (state.inventory_number + 1) % INVENTORY_SIZE[0]
            elif keys[state.controls[20]]:
                state.inventory_number = (state.inventory_number - 1) % INVENTORY_SIZE[0]
            for i in range(7, 19):
                if keys[state.controls[i]]:
                    state.inventory_number = i - 7

    state.tick += 1
    if state.tick % (DAY_LENGTH // 4) == 0:
        with open(path.join(SAVES_FOLDER, f"autosave_{(state.tick // (DAY_LENGTH // 4)) % 4}.txt"), "w", encoding="utf-8") as file:
                file.write(f"{chunks};{state.location['tile']};{state.tick};{state.noise_offset}")
    state.zoom = 0.05 * state.target_zoom + 0.95 * state.zoom
    return chunks