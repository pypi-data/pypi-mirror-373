from ...info import INVENTORY_SIZE


def take_out(chunks, location, inventory, slot_number, machine_inventory, singular):
    if slot_number < len(machine_inventory):
        item = list(machine_inventory.items())[slot_number]
        if singular:
            item = (item[0], 1)
        inventory_item = inventory.get(item[0], 0)
        if not (inventory_item == 0 and len(inventory) == INVENTORY_SIZE[0]):
            if inventory_item + item[1] <= INVENTORY_SIZE[1]:
                chunks[location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]]["inventory"][item[0]] = inventory_item + item[1]
                if not singular:
                    del chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]]
                else:
                    chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]] -= 1
                    if chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]] == 0:
                        del chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]]
            else:
                chunks[location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]]["inventory"][item[0]] = INVENTORY_SIZE[1]
                chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]] = inventory_item + item[1] - INVENTORY_SIZE[1]
        if chunks[location["opened"][0]][location["opened"][1]]["inventory"] == {}:
            del chunks[location["opened"][0]][location["opened"][1]]["inventory"]
    return chunks