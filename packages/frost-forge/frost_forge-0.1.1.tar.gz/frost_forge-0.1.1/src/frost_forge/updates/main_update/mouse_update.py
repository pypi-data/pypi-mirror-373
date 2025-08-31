from ...info import TILE_SIZE, ATTRIBUTES, RECIPES, INVENTORY_SIZE
from .right_click_updates import right_click
from .left_click_update import left_click

def button_press(button, position, zoom, chunks, location, machine_ui, inventory, health, machine_inventory, tick, inventory_number, recipe_number, camera):
    world_x = int((position[0] - camera[0]) // (TILE_SIZE * zoom))
    world_y = int((position[1] - camera[1]) // (TILE_SIZE * zoom))
    if (world_x - location["tile"][0] * 16 - location["tile"][2]) ** 2 + (world_y - location["tile"][1] * 16 - location["tile"][3]) ** 2 <= 20 or "open" in ATTRIBUTES.get(machine_ui, ()):
        grid_position = [(world_x // 16, world_y // 16), (world_x % 16, world_y % 16)]
        if grid_position[1] in chunks[grid_position[0]] and "kind" in chunks[grid_position[0]][grid_position[1]]:
            while "point" in ATTRIBUTES.get(chunks[grid_position[0]][grid_position[1]]["kind"], ()):
                if chunks[grid_position[0]][grid_position[1]]["kind"] == "left":
                    grid_position = [(grid_position[0][0] - (grid_position[1][0] == 0), grid_position[0][1]), ((grid_position[1][0] - 1) % 16, grid_position[1][1])]
                elif chunks[grid_position[0]][grid_position[1]]["kind"] == "up":
                    grid_position = [(grid_position[0][0], grid_position[0][1] - (grid_position[1][1] == 0)), (grid_position[1][0], (grid_position[1][1] - 1) % 16)]
                    
        if button == 1:
            machine_ui, chunks, location, machine_inventory, tick = left_click(machine_ui, grid_position, chunks, inventory_number, health, position, recipe_number, location, inventory, machine_inventory, tick)
        elif button == 3:
            chunks, location, machine_ui = right_click(chunks, grid_position, inventory, inventory_number, location, machine_ui)
    
    if button == 4 or button == 5:
        if "craft" in ATTRIBUTES.get(machine_ui, ()) or "machine" in ATTRIBUTES.get(machine_ui, ()):
            chunks[location["opened"][0]][location["opened"][1]]["recipe"] = (recipe_number + (button == 5) - (button == 4)) % len(RECIPES[machine_ui])
        else:
            inventory_number = (inventory_number + (button == 5) - (button == 4)) % INVENTORY_SIZE[0]
    return chunks, location, machine_ui, machine_inventory, tick, inventory_number