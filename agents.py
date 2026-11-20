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