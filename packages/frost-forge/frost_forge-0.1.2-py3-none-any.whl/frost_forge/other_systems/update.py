from .game_state import GameState
from ..updates import update_menu, update_game, update_tiles


def update(state: GameState, chunks):
    if state.menu_placement != "main_game":
        chunks = update_menu(state, chunks)
    else:
        chunks = update_game(state, chunks)
        chunks = update_tiles(state, chunks)
    return chunks