from ...world_generation.world_generation import generate_chunk

def save_creating(state, chunks):
    state.save_file_name = ""
    state.menu_placement = "main_game"
    chunks = {}
    state.location["tile"] = [0, 0, 0, 2]
    state.location["real"] = [0, 0, 0, 2]
    state.noise_offset = generate_chunk(state.world_type, 0, 0, chunks)
    for x in range(-4, 5):
        for y in range(-4, 5):
            generate_chunk(state.world_type, state.location["tile"][0] + x, state.location["tile"][1] + y, chunks, state.noise_offset)
    chunks[0, 0][0, 0] = {"kind": "obelisk", "health": 1}
    chunks[0, 0][0, 1] = {"kind": "up", "health": 1}
    chunks[0, 0][0, 2] = {"kind": "player", "inventory": {}, "health": 20, "floor": "void", "recipe": 0}
    if state.world_type == 1:
        chunks[0, 0][0, 2]["inventory"] = {"flint axe": 1}
        chunks[0, 0][0, 3] = {"kind": "tree", "floor": "dirt", "inventory": {"log": 2, "sapling": 2}}
        chunks[0, 0][0, 4] = {"kind": "composter"}
    state.tick = 0
    return chunks