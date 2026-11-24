# 2048-AI
CSE 352 Artificial Intelligence Course Project

## 1. Project Overview
- AI that automatically plays 2048 game. 
- Goal: Compare the tree decision in a situation containing uncertainty (random tiles)
- 4 Agents: Random, Minimax, Expectimax, Monte Carlo (MCTS)

## 2. Demo
- Link: https://mingu8908.github.io/2048-AI/
- Execute game.py / heuristics.py / agents.py by using Python in the browser. 
- Play directly with arrow keys (or WASD), or pick any AI of 4 to play one move or all of the moves. 
- Choice that can be picked: agent, depth(1~3), evaluation function (heuristic / just scores), number of MCTS rollouts, stop at 2048
- Bar Graph: Value that AI puts in each 4 directions. 

## 3. How to Execute
- Web Demo (Local)
    - cd web -> npm install -> npm run dev
- Test only game: python -c "from agents import make_agent, play_game; print(play_game(make_agent('expectimax', seed=0), seed=0))" -> Play with expectimax

## 4. Board Representation (same with every file)
- board = tuple with 16 numbers (starts with top left line by line)
- number is tile's log2 value: 0 = blank, 1 = 2, 2 = 4, ..., 11 = 2048
    - Storing log2 values keeps numbers small (2048 -> 11), makes a merge becomes just +1.
    - Heuristics are not hesitated by the big numbers. 
- Doesn't change because it is tuple -> can be used as key in dict (necessary for cache)

## 5. Function Description of Files
- game.py - 2048 game rule
    - DIRS: 4 directions ['up', 'down', 'left', 'right']
    - LINES: A table listing the cell numbers in the order they shift, with four rows per direction.
            so the 4 directions can be handled by one function (slide_line)
    - SLIDE_CACHE: store the line of already calculated
    - slide_line(line): slide one line (4 spaces), only merge once with same numbers. return (new line, earned points)
        - ex) (2, 2, 4, 0) -> (4, 4, 0, 0), 4 points (points = value of the new merged tile)
    - move(board, direction): move the whole board in one direction. return (new board, earned points). if new board == original board, that direction is the direction that cannot move. 
    - empty_cells(board): empty cell number list
    - place(board, cell, value): place a tile in one space and return new board
    - Game class: actual one game play
        - __init__(seed, board, score): prepare random generator (if seed is same same tile sequence), start with two tiles
        - spawn(board): place 2(prob 0.9) or 4(prob 0.1)
        - step(direction): move + spawn a new tile + add points. Returns None if the move is illegal.
        - over(): if the board cannot be moved in every four direction, it is game over. 
        - max_tile(): value of the largest tile (ex: 2048)
    - to_values(board): change log2 board into real number(for web screen)
    - render(board, score): print board in terminal in words

- heuristics.py - board evaluation function
    - ALL_FEATURES: all 5 feature name
    - WEIGHTS: weights per feature (empty 270, merges 700, monotonicity 47, smoothness 50, corner 2000)
    - get_lines(board): 4 lines of width + 4 lines of height = return 8 lines (other feature functions use)
    - count_empty(board): number of empty cells (better if many)
    - count_merges(board): tuple of numbers that can be merged immediately (better if many)
    - monotonicity_penalty(board): check how are each lines are out of ascending/descending order. 
        multiply 4 square the value and if the big tile is in the wrong place, penalty points get way bigger (better with small)
    - smoothness_penalty(board): sum of the difference with adjacent tiles (better with small, easy to merge)
    - corner_bonus(board): if the biggest tile is placed on of the four corners than that value, if not 0. 
    - eval_score_only(board, score): used to comparison. only use game scores. 
    - eval_heuristic(board, score, feature): weighted sum of active features. add good feature, remove penalty points
    - get_eval(name): select feature function by name. 'score', 'heuristic', 'no_<feature>'

- agents.py - AI agent
    - Commoness with every agents
        - Every agent has choose (board, score) -> (best direction, value of each direction). Illegal directions get None. 
    - DEATH: Value of game over board (very small number)
    - RandomAgent: Randomly picks one of moveable direction
    - MinimaxAgent: Suppose new tile always generates in worst space, worst number
        - choose: Top of the tree. calculate value of 4 directions and choose the biggest direction. initialize cache in every turn.
        - max_value: Node which is my turn. If depth is 0, calculate score with evaluation function, or biggest value of possible direcitons. If there is no moveable direction -> DEATH
        - chance_value: Tile node. Smallest number of every empty cell x {2, 4}. Here depth reduced to 1. 
        - cache (transposition table): Only caculate once with same (board, scores, depth, type of node)
    - ExpectimaxAgent (inherits minimax)
        - chance_value: probability-weighted average(expected value) of empty cell x {2: 0.9, 4: 0.1}. If the empty cell is more than 6, do the random sampling only 6 spaces. 
        - max_value: If the prob until here is less than 0.001, don't dig anymore and immediately evaluate (speed)
    - MCTSAgent (Monte Carlo): without heuristics
        - random_game(board): return the value by moving randomly until the game ends. 
        - choose: rollout N time (basically 100) by directions and choose the direction with highest average final score. 
    - make_agent(name, depth, eval_name, rollouts, seed): Create agent with name(string) (used at benchmark and web)
    - play_game(agent, seed): Play one game and return value, max tile, number, and average/max time by one move. 

- benchmark.py - experiment
    - EXPERIMENTS: 3 experiments and settings list per each experiment
        - algorithms: Random / Minimax d=3 / Expectimax d=3 / MCTS 100
        - depth: Expectimax d=1, 2, 3
        - heuristics: Expectimax d=3 + only scores / all five of them / five with one taken out of each
    - run_one(task): play one game and attach settings name and seed into result. seed = game number so all of the agents starts with same tile sequence (equivalent comparison)
    - summarize(label, rows): average score, highest score, prob to reach 2048/4096, average time per one move
    - save_csv(path, rows): stored into CSV
    - run_experiment(name, games): simultaneously execute all of the games by multiprocessing and multiple cores 
        -> summarize -> store into results/<Experiment>_games.csv, results/<Experiment>_summary.csv -> print tables

- web/ - Web Demo
    - Generated by Claude
    - Deployed through GitHub Pages

## 6. Experiment Results
- 10 games per setting, seeds 0-9 (every agent gets the same tile sequence)
- Run with: python benchmark.py <experiment> 10 (results saved in results/)
- Time per move was measured on my MacBook

### Experiment 1: Algorithms (depth 3)
- Random: mean 920, best 1,500, reach 2048 0%, reach 4096 0%, 0.000 s/move
- Minimax: mean 21,600, best 39,960, reach 2048 40%, reach 4096 0%, 0.611 s/move
- Expectimax: mean 44,321, best 89,424, reach 2048 90%, reach 4096 20%, 0.359 s/move
- MCTS (100 rollouts): mean 42,889, best 78,964, reach 2048 80%, reach 4096 40%, 0.343 s/move
- Result: Expectimax has the highest mean score and 2048 rate.
  Minimax assumes the worst tile every time, so it plays too carefully and scores about half of Expectimax.
  MCTS is almost as good without any heuristic and reached 4096 most often.

### Experiment 2: Search depth (Expectimax)
- Depth 1: mean 4,728, best 7,552, reach 2048 0%, 0.002 s/move
- Depth 2: mean 19,932, best 34,240, reach 2048 40%, 0.029 s/move
- Depth 3: mean 44,321, best 89,424, reach 2048 90%, 0.301 s/move
- Result: Each extra depth raises the score 2-4 times but makes each move about 10 times slower.
  Depth 3 is the deepest that is still fast enough for the live demo.

### Experiment 3: Evaluation function (Expectimax depth 3)
- Score only: mean 17,218, reach 2048 20%, reach 4096 0%
- All 5 features: mean 44,321, reach 2048 90%, reach 4096 20%
- No empty: mean 46,610, reach 2048 100%, reach 4096 20%
- No merges: mean 43,525, reach 2048 60%, reach 4096 40%
- No monotonicity: mean 33,700, reach 2048 80%, reach 4096 20%
- No smoothness: mean 42,990, reach 2048 80%, reach 4096 20%
- No corner: mean 50,689, reach 2048 80%, reach 4096 50%
- Result: The heuristic matters a lot (2.5 times higher than score only).
  Monotonicity is the most important feature: removing it drops the mean the most.
  Removing corner or empty did not hurt. Monotonicity already keeps the big tile in a corner, so the features overlap.
  With only 10 games, differences of a few thousand points may be noise.


## 7. Sources
- Heuristic features (empty, merges, monotonicity) and weights, 4 squared, statistics cutoff idea: nneonneo/2048-ai (https://github.com/nneonneo/2048-ai)
- smoothness, corner bonus weight added by myself
- Minimax, Expectimax, Monte Carlo rollout: CSE 352 lecture (Russell & Norvig, AIMA)
- Pyodide (Execute Python in browser), Vite (Web development server)
- The web UI was made with AI (allowed by Prof. Sun). 
- I used an AI assitant (Claude) to help write the code. I added it one function at a time, tested each part, and can explain all of it.
- The project idea, experiment design, and testing are my own. 