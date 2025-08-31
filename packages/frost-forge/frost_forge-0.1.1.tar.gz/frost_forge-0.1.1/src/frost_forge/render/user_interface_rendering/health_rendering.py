import pygame as pg

from ...info import SCREEN_SIZE, UI_SCALE, UI_FONT, HEALTH

def render_health(window, images, health):
    max_health = HEALTH["player"]
    window.blit(pg.transform.scale(images["health_bar"], (128 * UI_SCALE, 32 * UI_SCALE)), (SCREEN_SIZE[0] - 128 * UI_SCALE, 0))
    window.blit(pg.transform.scale(images["health_end"], (16 * UI_SCALE, 16 * UI_SCALE)), (SCREEN_SIZE[0] + (health * 64 / max_health - 96) * UI_SCALE, 8 * UI_SCALE))
    pg.draw.rect(window, (181, 102, 60), pg.Rect(SCREEN_SIZE[0] - 96 * UI_SCALE, 8 * UI_SCALE, health * 64 * UI_SCALE / max_health, 16 * UI_SCALE))
    window.blit(UI_FONT.render(f"{health} / {max_health}", False, (206, 229, 242)), (SCREEN_SIZE[0] - 80 * UI_SCALE, 12 * UI_SCALE))
    return window