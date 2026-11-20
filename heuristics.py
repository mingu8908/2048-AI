ALL_FEATURES = ['empty', 'merges', 'monotonicity', 'smoothness', 'corner']

WEIGHTS = {
    'empty': 270,
    'merges': 700,
    'monotonicity': 47,
    'smoothness': 50,
    'corner': 2000,
}

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

def corner_bonus(board):
    biggest = max(board)
    if biggest in (board[0], board[3], board[12], board[15]):
        return biggest
    return 0

def eval_score_only(board, score):
    return score


def eval_heuristic(board, score, features=ALL_FEATURES):
    value = 0
    if 'empty' in features:
        value += WEIGHTS['empty'] * count_empty(board)
    if 'merges' in features:
        value += WEIGHTS['merges'] * count_merges(board)
    if 'monotonicity' in features:
        value -= WEIGHTS['monotonicity'] * monotonicity_penalty(board)
    if 'smoothness' in features:
        value -= WEIGHTS['smoothness'] * smoothness_penalty(board)
    if 'corner' in features:
        value += WEIGHTS['corner'] * corner_bonus(board)
    return value


def get_eval(name):
    if name == 'score':
        return eval_score_only
    if name == 'heuristic':
        return eval_heuristic
    if name.startswith('no_') and name[3:] in ALL_FEATURES:
        on = [f for f in ALL_FEATURES if f != name[3:]]
        return lambda board, score: eval_heuristic(board, score, on)
    raise ValueError('unknown evaluation: ' + name)