from ...info import TILE_SIZE, HALF_SIZE, SCREEN_SIZE, MULTI_TILES, FLOOR


def render_ghost(position, camera, zoom, chunks, location, inventory, inventory_number, scaled_image, window):
    world_x = int((position[0] - camera[0]) // (TILE_SIZE * zoom))
    world_y = int((position[1] - camera[1]) // (TILE_SIZE * zoom))
    grid_position = [(world_x // 16, world_y // 16), (world_x % 16, world_y % 16)]
    if inventory_number < len(inventory):
        if grid_position[0] in chunks:
            if (world_x - location["tile"][0] * 16 - location["tile"][2]) ** 2 + (world_y - location["tile"][1] * 16 - location["tile"][3]) ** 2 <= 10:
                inventory_key = list(inventory.keys())[inventory_number]
                size = MULTI_TILES.get(inventory_key, (1, 1))
                if -TILE_SIZE * zoom * size[0] <= world_x <= SCREEN_SIZE[0] and -TILE_SIZE * zoom * size[1] * 3 / 2 <= world_y <= SCREEN_SIZE[1] and inventory_number < len(inventory):
                    placement = (camera[0] + world_x * TILE_SIZE * zoom, camera[1] + (world_y * TILE_SIZE - HALF_SIZE) * zoom,)
                    alpha_image = scaled_image[inventory_key].copy()
                    alpha_image.set_alpha(85)
                    if inventory_key in FLOOR:
                        window.blit(alpha_image, (placement[0], placement[1] + HALF_SIZE * zoom))
                    else:
                        window.blit(alpha_image, placement)
    return window