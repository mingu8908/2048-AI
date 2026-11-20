import random
import time

from game import DIRS, move, empty_cells, place
from heuristics import eval_heuristic

DEATH = -1000000


class RandomAgent:
    name = 'Random'

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.last_time = 0.0

    def choose(self, board, score=0):
        start = time.time()
        scores = {}
        for d in DIRS:
            new_board, gain = move(board, d)
            scores[d] = None if new_board == board else 0
        legal = [d for d in DIRS if scores[d] is not None]
        best = self.rng.choice(legal) if legal else None
        if best:
            scores[best] = 1
        self.last_time = time.time() - start
        return best, scores

class MinimaxAgent:
    def __init__(self, depth=3, eval_fn=eval_heuristic, seed=None):
        self.depth = depth
        self.eval_fn = eval_fn
        self.rng = random.Random(seed)
        self.cache = {}
        self.last_time = 0.0
        self.name = 'Minimax'

    def max_value(self, board, score, depth, prob):
        if depth == 0:
            return self.eval_fn(board, score)
        key = (board, score, depth, 'max')
        if key in self.cache:
            return self.cache[key]
        best = None
        for d in DIRS:
            new_board, gain = move(board, d)
            if new_board != board:
                value = self.chance_value(new_board, score + gain, depth, prob)
                if best is None or value > best:
                    best = value
        if best is None:
            best = DEATH
        self.cache[key] = best
        return best

    def chance_value(self, board, score, depth, prob):
        key = (board, score, depth, 'chance')
        if key in self.cache:
            return self.cache[key]
        worst = None
        for cell in empty_cells(board):
            for tile in (1, 2):
                value = self.max_value(place(board, cell, tile), score, depth - 1, prob)
                if worst is None or value < worst:
                    worst = value
        self.cache[key] = worst
        return worst