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

    def choose(self, board, score=0):
        start = time.time()
        self.cache = {}
        scores = {}
        for d in DIRS:
            new_board, gain = move(board, d)
            if new_board == board:
                scores[d] = None
            else:
                scores[d] = self.chance_value(new_board, score + gain, self.depth, 1.0)
        best = None
        for d in DIRS:
            if scores[d] is not None and (best is None or scores[d] > scores[best]):
                best = d
        self.last_time = time.time() - start
        return best, scores

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

class ExpectimaxAgent(MinimaxAgent):
    def __init__(self, depth=3, eval_fn=eval_heuristic, max_cells=6, min_prob=0.001, seed=None):
        super().__init__(depth, eval_fn, seed)
        self.max_cells = max_cells
        self.min_prob = min_prob
        self.name = 'Expectimax'

    def max_value(self, board, score, depth, prob):
        if prob < self.min_prob:
            return self.eval_fn(board, score)
        return super().max_value(board, score, depth, prob)

    def chance_value(self, board, score, depth, prob):
        key = (board, score, depth, 'chance')
        if key in self.cache:
            return self.cache[key]
        cells = empty_cells(board)
        if len(cells) > self.max_cells:
            cells = self.rng.sample(cells, self.max_cells)
        total = 0
        for cell in cells:
            p_cell = 1 / len(cells)
            total += p_cell * 0.9 * self.max_value(place(board, cell, 1), score, depth - 1, prob * p_cell * 0.9)
            total += p_cell * 0.1 * self.max_value(place(board, cell, 2), score, depth - 1, prob * p_cell * 0.1)
        self.cache[key] = total
        return total

class MCTSAgent:
    def __init__(self, rollouts=100, seed=None):
        self.rollouts = rollouts
        self.rng = random.Random(seed)
        self.last_time = 0.0
        self.name = 'MCTS'

    def random_game(self, board):
        points = 0
        while True:
            moves = []
            for d in DIRS:
                new_board, gain = move(board, d)
                if new_board != board:
                    moves.append((new_board, gain))
            if not moves:
                return points
            new_board, gain = self.rng.choice(moves)
            points += gain
            cell = self.rng.choice(empty_cells(new_board))
            tile = 1 if self.rng.random() < 0.9 else 2
            board = place(new_board, cell, tile)

    def choose(self, board, score=0):
        start = time.time()
        scores = {}
        for d in DIRS:
            new_board, gain = move(board, d)
            if new_board == board:
                scores[d] = None
                continue
            total = 0
            for _ in range(self.rollouts):
                cell = self.rng.choice(empty_cells(new_board))
                tile = 1 if self.rng.random() < 0.9 else 2
                total += gain + self.random_game(place(new_board, cell, tile))
            scores[d] = score + total / self.rollouts
        best = None
        for d in DIRS:
            if scores[d] is not None and (best is None or scores[d] > scores[best]):
                best = d
        self.last_time = time.time() - start
        return best, scores