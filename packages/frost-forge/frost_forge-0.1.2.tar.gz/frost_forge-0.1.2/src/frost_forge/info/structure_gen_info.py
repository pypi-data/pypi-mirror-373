NOISE_STRUCTURES = {
    "forest": (
        ((0, 0.05), "mushroom hut"),
    ),
    "plains": (
        ((0, 0), "copper dungeon"),
    ),
}
ROOM_COLORS = {
    (247, 247, 255): {"kind": "mushroom block", "floor": "mushroom floor"},
    (138, 138, 140): {"floor": "mushroom floor"},
    (53, 53, 54): {"floor": "mushroom door"},
    (106, 228, 138): {"kind": "mushroom shaper", "floor": "mushroom floor"},
    (92, 74, 49): {"kind": "small crate", "loot": "mushroom chest", "floor": "mushroom floor"},
    (136, 68, 31): {"kind": "copper brick", "floor": "copper brick floor"},
    (181, 102, 60): {"floor": "copper brick floor"},
}
STRUCTURE_ENTRANCE = {"copper dungeon": {"kind": "glass lock"}, "mushroom hut": {"floor": "mushroom door"}}
STRUCTURE_ROOM_SIZES = {"copper dungeon": ((1, 1), (2, 1), (2, 2)), "mushroom hut": ((1, 1),)}
STRUCTURE_SIZE = {"copper dungeon": 0.8, "mushroom hut": 0}
STRUCTURE_ROOMS = {
    "copper dungeon": {
        (1, 1): ("treasury", "hallway"),
        (2, 1): ("library", "banquet"),
        (2, 2): ("forge",),
    },
    "mushroom hut": {
        (1, 1): ("mushroom hut",),
    },
}
LOOT_TABLES = {
    "mushroom chest": {
        (0.7, "spore", 1, 5),
        (0.6, "mushroom", 2, 7),
        (0.4, "mushroom block", 3, 5),
        (0.25, "fertilizer", 1, 2),
        (0.2, "mushroom floor", 2, 3),
        (0.15, "plant bouquet", 1, 3),
        (0.1, "mushroom shaper", 1, 1),
        (0.05, "mushroom door", 1, 2),
        (0.03, "composter", 1, 1),
        (0.02, "bonsai pot", 1, 2),
    }
}