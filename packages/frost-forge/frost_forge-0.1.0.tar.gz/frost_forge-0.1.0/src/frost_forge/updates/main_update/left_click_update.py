from ...info import ATTRIBUTES, DAY_LENGTH, FLOOR_TYPE
from ..left_click import recipe, place, open_storage, closed_storage, machine_storage, unlock, fertilize_grow, fertilize_spawn


def left_click(
    machine_ui: str,
    grid_position: list[int, int],
    chunks,
    inventory_number: int,
    health: int,
    position,
    recipe_number: int,
    location: dict[str],
    inventory: dict[str, int],
    machine_inventory: dict[str, int],
    tick: int,
):
    if machine_ui == "game":
        is_not_tile = (grid_position[1] not in chunks[grid_position[0]])
        if is_not_tile:
            is_kind = True
        else:
            is_kind = "kind" in chunks[grid_position[0]][grid_position[1]]
            current_tile = chunks[grid_position[0]][grid_position[1]]
        is_floor = not is_not_tile and not is_kind
        if is_floor and FLOOR_TYPE.get(current_tile["floor"]) == "door":
            chunks[grid_position[0]][grid_position[1]]["floor"] += " open"
        elif is_floor and FLOOR_TYPE.get(current_tile["floor"]) == "open":
            chunks[grid_position[0]][grid_position[1]]["floor"] = current_tile["floor"][:-5]
        elif is_floor and FLOOR_TYPE.get(current_tile["floor"]) == "soil" and inventory_number < len(inventory) and "fertilize" in ATTRIBUTES.get(list(inventory.keys())[inventory_number], ()):
            chunks = fertilize_spawn(chunks, inventory, inventory_number, grid_position)
        elif is_not_tile or not is_kind:
            chunks = place(inventory, inventory_number, is_not_tile, is_kind, health, grid_position, location, chunks)
        else:
            attributes = ATTRIBUTES.get(chunks[grid_position[0]][grid_position[1]]["kind"], ())
            if "open" in attributes:
                machine_ui = chunks[grid_position[0]][grid_position[1]]["kind"]
                location["opened"] = (grid_position[0], grid_position[1])
                machine_inventory = chunks[grid_position[0]][grid_position[1]].get("inventory", {})
            elif "sleep" in attributes:
                if 9 / 16 <= (tick / DAY_LENGTH) % 1 < 15 / 16:
                    tick = (tick // DAY_LENGTH + 9 / 16) * DAY_LENGTH
            elif "lock" in attributes:
                chunks = unlock(inventory, inventory_number, chunks, grid_position)
            elif "grow" in attributes and inventory_number < len(inventory):
                chunks = fertilize_grow(chunks, inventory, inventory_number, grid_position)
            elif "store" in attributes:
                chunks = closed_storage(chunks, grid_position, inventory, location, inventory_number)
    elif "machine" in ATTRIBUTES.get(machine_ui, ()):
        chunks = machine_storage(position, chunks, location, inventory, machine_ui)
    elif "store" in ATTRIBUTES.get(machine_ui, ()):
        chunks = open_storage(position, chunks, location, inventory, machine_ui)
    elif "craft" in ATTRIBUTES.get(machine_ui, ()):
        inventory = recipe(machine_ui, recipe_number, inventory)
    return machine_ui, chunks, location, machine_inventory, tick
