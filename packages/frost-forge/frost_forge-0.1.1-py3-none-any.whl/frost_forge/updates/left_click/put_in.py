def put_in(chunks, location, inventory, machine_storage, slot_number, machine_inventory):
    if slot_number < len(inventory):
        item = list(inventory.items())[slot_number]
        machine_item = machine_inventory.get(item[0], 0)
        if not (machine_item == 0 and len(machine_inventory) == machine_storage[0]):
            if machine_item + item[1] <= machine_storage[1]:
                chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]] = machine_item + item[1]
                del chunks[location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]]["inventory"][item[0]]
            else:
                chunks[location["opened"][0]][location["opened"][1]]["inventory"][item[0]] = machine_storage[1]
                chunks[location["tile"][0], location["tile"][1]][location["tile"][2], location["tile"][3]]["inventory"][item[0]] = (machine_item + item[1] - machine_storage[1])
    return chunks