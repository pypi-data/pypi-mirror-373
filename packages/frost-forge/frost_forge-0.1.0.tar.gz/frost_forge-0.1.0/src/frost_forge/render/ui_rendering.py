import pygame as pg

from .user_interface_rendering import render_health, render_inventory, render_open

def render_ui(inventory_number, inventory, machine_ui, recipe_number, health, machine_inventory, window, images):
    window = render_health(window, images, health)
    window = render_inventory(inventory_number, window, images, inventory)
    window = render_open(machine_ui, window, images, recipe_number, machine_inventory)
    return window