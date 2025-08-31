from ...info import INVENTORY_SIZE, HEALTH
from .damage_calculation import calculate_damage

def break_floor(mining_tile, inventory, inventory_number, player_tile):
    delete_mining_tile = False
    if "health" not in mining_tile:
        mining_tile["health"] = HEALTH[mining_tile["floor"]]
    mining_tile["health"] -= calculate_damage(mining_tile["floor"], inventory, inventory_number)
    broke = False
    if mining_tile["health"] <= 0:
        if mining_tile["floor"] in inventory:
            if inventory[mining_tile["floor"]] < INVENTORY_SIZE[1]:
                broke = True
        elif len(inventory) < INVENTORY_SIZE[0]:
            broke = True
    if broke:
        player_tile["inventory"][mining_tile["floor"]] = player_tile["inventory"].get(mining_tile["floor"], 0) + 1
        delete_mining_tile = True
    return delete_mining_tile, inventory, mining_tile