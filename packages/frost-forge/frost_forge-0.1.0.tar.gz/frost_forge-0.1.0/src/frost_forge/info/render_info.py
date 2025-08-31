import pygame as pg

pg.display.init()
pg.font.init()

SCREEN_SIZE = (pg.display.Info().current_w, pg.display.Info().current_h)
TILE_SIZE = 64
HALF_SIZE = TILE_SIZE // 2
CHUNK_SIZE = 16 * TILE_SIZE
FPS = 60
DAY_LENGTH = 60 * 24 * FPS
UI_SCALE = 2
UI_FONT = pg.font.SysFont("Lucida Console", 10 * UI_SCALE)
BIG_UI_FONT = pg.font.SysFont("Lucida Console", 20 * UI_SCALE)
SLOT_SIZE = (32 * UI_SCALE, 32 * UI_SCALE)
TILE_UI_SIZE = (16 * UI_SCALE, 24 * UI_SCALE)
FLOOR_SIZE = (16 * UI_SCALE, 16 * UI_SCALE)
HALF_SCREEN_SIZE = SCREEN_SIZE[0] // 2
INVENTORY_SIZE = (12, 64)