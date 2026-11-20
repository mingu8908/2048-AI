def get_lines(board):
    rows = [list(board[r * 4: r * 4 + 4]) for r in range(4)]
    cols = [[board[r * 4 + c] for r in range(4)] for c in range(4)]
    return rows + cols


def count_empty(board):
    return board.count(0)