from ...info import SCREEN_SIZE, UI_SCALE, INVENTORY_SIZE, RECIPES, ATTRIBUTES, MACHINES, VALUES
from .put_in import put_in
from .take_out import take_out

def machine_storage(position, chunks, location, inventory, machine_ui):
    if "inventory" not in chunks[location["opened"][0]][location["opened"][1]]:
        chunks[location["opened"][0]][location["opened"][1]]["inventory"] = {}
    moved_x = position[0] - SCREEN_SIZE[0] // 2
    machine = chunks[location["opened"][0]][location["opened"][1]]
    machine_recipe = RECIPES[machine_ui][machine.get("recipe", 0)]
    holding_over_inventory = position[1] >= SCREEN_SIZE[1] - 32 * UI_SCALE and abs(moved_x) <= 16 * INVENTORY_SIZE[0] * UI_SCALE
    if holding_over_inventory:
        inventory_number = ((moved_x - 16 * UI_SCALE * (INVENTORY_SIZE[0] % 2)) // (32 * UI_SCALE) + INVENTORY_SIZE[0] // 2 + INVENTORY_SIZE[0] % 2)
        if inventory_number < len(inventory):
            item = list(inventory.items())[((moved_x - 16 * UI_SCALE * (INVENTORY_SIZE[0] % 2)) // (32 * UI_SCALE) + INVENTORY_SIZE[0] // 2 + INVENTORY_SIZE[0] % 2)]
            may_put_in = False
            convert = False
            for i in range(0, len(machine_recipe[1])):
                if machine_recipe[1][i][0] == item[0]:
                    may_put_in = True
            if "value" in ATTRIBUTES[machine["kind"]]:
                if item[0] in VALUES[MACHINES[machine["kind"]]]:
                    may_put_in = True
                    convert = True
            if may_put_in:
                chunks = put_in(chunks, location, inventory, machine_ui, moved_x, machine["inventory"])
                if convert:
                    chunks[location["opened"][0]][location["opened"][1]]["inventory"][MACHINES[machine["kind"]]] = VALUES[MACHINES[machine["kind"]]][item[0]] * machine["inventory"][item[0]]
                    del chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]]
    slot_row = (position[1] - SCREEN_SIZE[1] + 144 * UI_SCALE) // (32 * UI_SCALE)
    if slot_row == 2 and (moved_x + 112 * UI_SCALE) // (32 * UI_SCALE) == 0:
        item = (machine_recipe[0][0], machine["inventory"].get(machine_recipe[0][0], 0))
        if machine["inventory"].get(item[0], 0) > 0:
            chunks = take_out(chunks, location, inventory, item)
    return chunks