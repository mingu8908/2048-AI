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

def summarize(label, rows):
    n = len(rows)
    scores = [r['score'] for r in rows]
    return {
        'config': label,
        'games': n,
        'mean_score': round(sum(scores) / n),
        'best_score': max(scores),
        'reach_2048_pct': round(100 * sum(r['max_tile'] >= 2048 for r in rows) / n),
        'reach_4096_pct': round(100 * sum(r['max_tile'] >= 4096 for r in rows) / n),
        'sec_per_move': round(sum(r['sec_per_move'] for r in rows) / n, 3),
    }

def save_csv(path, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def run_one(task):
    label, name, kwargs, seed = task
    agent = make_agent(name, seed=seed, **kwargs)
    result = play_game(agent, seed=seed)
    result['config'] = label
    result['seed'] = seed
    return result

def run_experiment(name, games):
    configs = EXPERIMENTS[name]
    tasks = []
    for label, agent_name, kwargs in configs:
        for seed in range(games):
            tasks.append((label, agent_name, kwargs, seed))
    with Pool() as pool:
        results = pool.map(run_one, tasks)
    summaries = []
    for label, agent_name, kwargs in configs:
        rows = [r for r in results if r['config'] == label]
        summaries.append(summarize(label, rows))
    os.makedirs('results', exist_ok=True)
    save_csv('results/%s_games.csv' % name, results)
    save_csv('results/%s_summary.csv' % name, summaries)
    print('\n' + name)
    for s in summaries:
        print('%-20s mean %7d  best %7d  2048: %3d%%  4096: %3d%%  %.3f s/move' % (
            s['config'], s['mean_score'], s['best_score'],
            s['reach_2048_pct'], s['reach_4096_pct'], s['sec_per_move']))


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'algorithms'
    games = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    if name == 'all':
        for exp in EXPERIMENTS:
            run_experiment(exp, games)
    else:
        run_experiment(name, games)