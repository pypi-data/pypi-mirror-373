from ...info.tile_info import PROCESSING_TIME
from ..left_click import recipe


def machine(chunks, chunk, tile, current_tile, tick):
    if tick % PROCESSING_TIME[current_tile["kind"]] == 0:
        chunks[chunk][tile]["inventory"] = recipe(current_tile["kind"], current_tile.get("recipe", 0), current_tile.get("inventory", {}))
    return chunks