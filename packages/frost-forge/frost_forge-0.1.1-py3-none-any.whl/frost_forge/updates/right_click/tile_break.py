from ...info import INVENTORY_SIZE, HEALTH, ATTRIBUTES
from .damage_calculation import calculate_damage

def break_tile(mining_kind, inventory, player_tile, chunks, mining_tile, inventory_number):
    delete_mining_tile = False
    if mining_kind != "player":
        if "health" not in mining_tile:
            mining_tile["health"] = HEALTH[mining_tile["kind"]]
        mining_tile["health"] -= calculate_damage(mining_tile["kind"], inventory, inventory_number)
        if mining_tile["health"] <= 0:
            mining_floor_exist = "floor" in mining_tile
            if mining_floor_exist:
                mining_floor = mining_tile["floor"]
            if mining_kind != "player":
                junk_inventory = {}
                if "no_pickup" not in ATTRIBUTES.get(mining_tile["kind"], ()):
                    inventory[mining_kind] = inventory.get(mining_kind, 0) + 1
                if "inventory" in mining_tile:
                    for item, amount in mining_tile["inventory"].items():
                        if item in player_tile["inventory"]:
                            player_tile["inventory"][item] += amount
                            if inventory[item] > INVENTORY_SIZE[1]:
                                junk_inventory[item] = player_tile["inventory"][item] - INVENTORY_SIZE[1]
                                player_tile["inventory"][item] = INVENTORY_SIZE[1]
                        else:
                            if len(inventory) < INVENTORY_SIZE[0]:
                                player_tile["inventory"][item] = amount
                            else:
                                junk_inventory[item] = amount
                if mining_floor_exist:
                    mining_tile = {}
                else:
                    delete_mining_tile = True
                if len(junk_inventory) > 0:
                    mining_tile = {"kind": "junk", "inventory": junk_inventory}
            if mining_floor_exist:
                mining_tile["floor"] = mining_floor
    return chunks, delete_mining_tile, mining_tile