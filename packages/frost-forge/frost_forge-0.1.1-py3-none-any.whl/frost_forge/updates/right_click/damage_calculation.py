from ...info import RESISTANCE, TOOL_EFFICIENCY, TOOL_REQUIRED

def calculate_damage(mining_type, inventory, inventory_number):
    damage = 1 - RESISTANCE.get(mining_type, 0)
    if len(inventory) > inventory_number:
        inventory_words = list(inventory.keys())[inventory_number].split()
        if len(inventory_words) == 2 and mining_type in TOOL_REQUIRED:
            if TOOL_REQUIRED[mining_type] == inventory_words[1]:
                damage += TOOL_EFFICIENCY[inventory_words[0]]
    return max(damage, 0)