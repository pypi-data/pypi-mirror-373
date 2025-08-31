from ...info import RECIPES, INVENTORY_SIZE

def recipe(machine_ui: str, recipe_number: int, inventory: dict[str, int],):
    output_item, output_amount = RECIPES[machine_ui][recipe_number][0]
    input = RECIPES[machine_ui][recipe_number][1]
    if (len(inventory) >= INVENTORY_SIZE[0] and inventory.get(output_item, 0) + output_amount >= INVENTORY_SIZE[1]):
        return inventory
    for i in range(0, len(input)):
        if input[i][0] not in inventory or inventory[input[i][0]] < input[i][1]:
            return inventory
    for i in range(0, len(input)):
        inventory[input[i][0]] -= input[i][1]
        if inventory[input[i][0]] <= 0:
            del inventory[input[i][0]]
    inventory[output_item] = inventory.get(output_item, 0) + output_amount
    return inventory