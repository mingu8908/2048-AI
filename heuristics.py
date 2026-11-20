def get_lines(board):
    rows = [list(board[r * 4: r * 4 + 4]) for r in range(4)]
    cols = [[board[r * 4 + c] for r in range(4)] for c in range(4)]
    return rows + cols

def count_empty(board):
    return board.count(0)

def count_merges(board):
    pairs = 0
    for line in get_lines(board):
        tiles = [x for x in line if x != 0]
        i = 0
        while i < len(tiles) - 1:
            if tiles[i] == tiles[i + 1]:
                pairs += 1
                i += 2
            else:
                i += 1
    return pairs

def monotonicity_penalty(board):
    total = 0
    for line in get_lines(board):
        up = 0
        down = 0
        for i in range(3):
            a = line[i] ** 4
            b = line[i + 1] ** 4
            if a > b:
                down += a - b
            else:
                up += b - a
        total += min(up, down)
    return total

def smoothness_penalty(board):
    total = 0
    for line in get_lines(board):
        tiles = [x for x in line if x != 0]
        for i in range(len(tiles) - 1):
            total += abs(tiles[i] - tiles[i + 1])
    return total