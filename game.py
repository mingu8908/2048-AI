import random

DIRS = ['up', 'down', 'left', 'right']

LINES = {
    'left':  [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]],
    'right': [[3, 2, 1, 0], [7, 6, 5, 4], [11, 10, 9, 8], [15, 14, 13, 12]],
    'up':    [[0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15]],
    'down':  [[12, 8, 4, 0], [13, 9, 5, 1], [14, 10, 6, 2], [15, 11, 7, 3]],
}

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

def move(board, direction):
    new = list(board)
    points = 0
    for idx in LINES[direction]:
        line = tuple(board[i] for i in idx)
        new_line, p = slide_line(line)
        for i, v in zip(idx, new_line):
            new[i] = v
        points += p
    return tuple(new), points

def empty_cells(board):
    return [i for i in range(16) if board[i] == 0]


def place(board, cell, value):
    new = list(board)
    new[cell] = value
    return tuple(new)