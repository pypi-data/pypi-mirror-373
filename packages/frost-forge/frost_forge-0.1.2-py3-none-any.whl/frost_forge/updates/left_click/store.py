from ...info import SCREEN_SIZE, INVENTORY_SIZE, UI_SCALE, STORAGE
from .put_in import put_in
from .take_out import take_out


def open_storage(position, chunks, location, inventory, machine_ui, singular = False):
    moved_x = position[0] - SCREEN_SIZE[0] // 2
    if "inventory" not in chunks[location["opened"][0]][location["opened"][1]]:
        chunks[location["opened"][0]][location["opened"][1]]["inventory"] = {}
    machine_inventory = chunks[location["opened"][0]][location["opened"][1]]["inventory"]
    holding_over_inventory = position[1] >= SCREEN_SIZE[1] - 32 * UI_SCALE and abs(moved_x) <= 16 * INVENTORY_SIZE[0] * UI_SCALE
    if holding_over_inventory:
        slot_number = ((moved_x - 16 * UI_SCALE * (INVENTORY_SIZE[0] % 2)) // (32 * UI_SCALE) + INVENTORY_SIZE[0] // 2 + INVENTORY_SIZE[0] % 2)
        machine_storage = STORAGE.get(machine_ui, (14, 16))
        chunks = put_in(chunks, location, inventory, machine_storage, slot_number, machine_inventory, singular)
    elif (SCREEN_SIZE[1] - 144 * UI_SCALE <= position[1] <= SCREEN_SIZE[1] - 80 * UI_SCALE and abs(moved_x) <= 112 * UI_SCALE):
        slot_number = (moved_x + 112 * UI_SCALE) // (32 * UI_SCALE) + (position[1] - SCREEN_SIZE[1] + 144 * UI_SCALE) // (32 * UI_SCALE) * 7
        chunks = take_out(chunks, location, inventory, slot_number, machine_inventory, singular)
    return chunks, machine_inventory

def closed_storage(chunks, grid_position, inventory, location, inventory_number):
    location["opened"] = (grid_position[0], grid_position[1])
    if "inventory" in chunks[grid_position[0]][grid_position[1]]:
        take_out(chunks, location, inventory, list(chunks[grid_position[0]][grid_position[1]]["inventory"].items())[0])
    elif inventory_number < len(inventory):
        chunks[grid_position[0]][grid_position[1]]["inventory"] = {}
        put_in(chunks, location, inventory, (1, 64), inventory_number, {})
    return chunks