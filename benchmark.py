import csv
import os
import sys
from multiprocessing import Pool

from agents import make_agent, play_game

EXPERIMENTS = {
    'algorithms': [
        ('Random', 'random', {}),
        ('Minimax d=3', 'minimax', {'depth': 3}),
        ('Expectimax d=3', 'expectimax', {'depth': 3}),
        ('MCTS 100 rollouts', 'mcts', {'rollouts': 100}),
    ],
    'depth': [
        ('Expectimax d=1', 'expectimax', {'depth': 1}),
        ('Expectimax d=2', 'expectimax', {'depth': 2}),
        ('Expectimax d=3', 'expectimax', {'depth': 3}),
    ],
    'heuristics': [
        ('Score only', 'expectimax', {'eval_name': 'score'}),
        ('All 5 features', 'expectimax', {'eval_name': 'heuristic'}),
        ('No empty', 'expectimax', {'eval_name': 'no_empty'}),
        ('No merges', 'expectimax', {'eval_name': 'no_merges'}),
        ('No monotonicity', 'expectimax', {'eval_name': 'no_monotonicity'}),
        ('No smoothness', 'expectimax', {'eval_name': 'no_smoothness'}),
        ('No corner', 'expectimax', {'eval_name': 'no_corner'}),
    ],
}


def run_one(task):
    label, name, kwargs, seed = task
    agent = make_agent(name, seed=seed, **kwargs)
    result = play_game(agent, seed=seed)
    result['config'] = label
    result['seed'] = seed
    return result