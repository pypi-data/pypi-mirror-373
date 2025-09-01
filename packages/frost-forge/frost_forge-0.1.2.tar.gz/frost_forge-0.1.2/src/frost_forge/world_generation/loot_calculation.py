from random import random, randint

from ..info import LOOT_TABLES


def calculate_loot(tile):
    loot_table = LOOT_TABLES[tile["loot"]]
    tile["inventory"] = {}
    for item in loot_table:
        if random() < item[0]:
            tile["inventory"][item[1]] = randint(item[2], item[3])
    if len(tile["inventory"]) <= 1:
        tile = calculate_loot(tile)
    return tile