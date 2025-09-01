import pygame as pg

from ...info import TILE_SIZE


def render_border(chunk, x, y, chunks, placement, zoom, window, current_tile):
    total_x = chunk[0] * 16 + x
    total_y = chunk[1] * 16 + y
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        adjacent_chunk = ((total_x + dx) // 16, (total_y + dy) // 16)
        adjacent_tile = ((total_x + dx) % 16, (total_y + dy) % 16)
        if adjacent_tile not in chunks[adjacent_chunk] or "floor" not in chunks[adjacent_chunk][adjacent_tile] or chunks[adjacent_chunk][adjacent_tile]["floor"] != current_tile["floor"]:
            if dx != 0 and dy != 0:
                rect = pg.Rect(placement[0] + ((TILE_SIZE - 2) * zoom if dx == 1 else 0), placement[1] + ((TILE_SIZE - 2) * zoom if dy == 1 else 0), zoom * 4, zoom * 4)
            elif dx != 0:
                rect = pg.Rect(placement[0] + dx * (TILE_SIZE - 2) * zoom if dx == 1 else placement[0], placement[1], zoom * 4, (TILE_SIZE + 2) * zoom)
            else:
                rect = pg.Rect(placement[0], placement[1] + dy * (TILE_SIZE - 2) * zoom if dy == 1 else placement[1], (TILE_SIZE + 2) * zoom, zoom * 4)
            pg.draw.rect(window, (19, 17, 18), rect)