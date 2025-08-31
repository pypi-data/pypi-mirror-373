from ..right_click import break_tile, break_floor
from ...info import UNBREAK

def right_click(
    chunks,
    grid_position: tuple[tuple[int, int], tuple[int, int]],
    inventory: dict[str, int],
    inventory_number: int,
    location: dict,
    machine_ui: str,
):
    machine_ui = "game"
    if grid_position[1] not in chunks[grid_position[0]]:
        return chunks, location, machine_ui
    mining_tile = chunks[grid_position[0]][grid_position[1]]
    delete_mining_tile = False
    player_tile = chunks[location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]]
    location["mined"] = (grid_position[0], grid_position[1])
    if "kind" in mining_tile and mining_tile["kind"] not in UNBREAK:
        chunks, delete_mining_tile, mining_tile = break_tile(mining_tile["kind"], inventory, player_tile, chunks, mining_tile, inventory_number)
    elif "floor" in mining_tile and mining_tile["floor"] not in UNBREAK:
        delete_mining_tile, inventory, mining_tile = break_floor(mining_tile, inventory, inventory_number, player_tile)
    chunks[location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]] = player_tile
    if delete_mining_tile:
        del chunks[grid_position[0]][grid_position[1]]
    else:
        chunks[grid_position[0]][grid_position[1]] = mining_tile
    return chunks, location, machine_ui