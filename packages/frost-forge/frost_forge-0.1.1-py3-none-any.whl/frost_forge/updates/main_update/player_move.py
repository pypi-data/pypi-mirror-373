def move_player(key, controls, velocity, location):
    if key[controls[24]]:
        speed = 0.07
    else:
        speed = 0.1
    if key[controls[0]]:
        velocity[1] -= speed / (1 + abs(velocity[1]))
    if key[controls[1]]:
        velocity[0] -= speed / (1 + abs(velocity[1]))
    if key[controls[2]]:
        velocity[1] += speed / (1 + abs(velocity[1]))
    if key[controls[3]]:
        velocity[0] += speed / (1 + abs(velocity[1]))
    location["real"][2] += velocity[0] / 2
    location["real"][3] += velocity[1] / 2
    velocity[0] *= 0.65
    velocity[1] *= 0.65
    location["real"] = [
        location["real"][0] + location["real"][2] // 16,
        location["real"][1] + location["real"][3] // 16,
        location["real"][2] % 16,
        location["real"][3] % 16,
    ]
    location["tile"] = [
        int(location["real"][0]),
        int(location["real"][1]),
        int(location["real"][2]),
        int(location["real"][3]),
    ]
    return (location, velocity)
