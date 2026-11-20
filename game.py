import random


def slide_line(line):
    tiles = [x for x in line if x != 0]
    result = []
    points = 0
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            result.append(tiles[i] + 1)
            points += 2 ** (tiles[i] + 1)
            i += 2
        else:
            result.append(tiles[i])
            i += 1
    result += [0] * (4 - len(result))
    return tuple(result), points