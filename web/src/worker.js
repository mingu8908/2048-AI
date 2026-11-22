// Web Worker: runs Pyodide and the Python files (game.py, heuristics.py, agents.py)
// so the page never freezes while the AI is thinking.

const PY_FILES = ['game.py', 'heuristics.py', 'agents.py'];

// Small Python layer between the page and the AI code. Everything is sent as JSON.
const GLUE = `
import json
import game
from agents import make_agent

G = None

def state(extra=None):
    s = {'board': game.to_values(G.board), 'score': G.score, 'moves': G.n_moves,
         'max_tile': G.max_tile(), 'over': G.over()}
    if extra:
        s.update(extra)
    return json.dumps(s)

def new_game():
    global G
    G = game.Game()
    return state()

def human_move(direction):
    gain = G.step(direction)
    return state({'gain': gain, 'illegal': gain is None})

def ai_move(name, depth, eval_name, rollouts):
    agent = make_agent(name, depth=depth, eval_name=eval_name, rollouts=rollouts)
    best, scores = agent.choose(G.board, G.score)
    if best is None:
        return state({'best': None, 'scores': scores, 'time': 0})
    gain = G.step(best)
    return state({'best': best, 'scores': scores, 'time': agent.last_time, 'gain': gain})
`;

let py = null;

async function init() {
  // Pyodide lives in public/pyodide (copied there by copy-files.mjs). The URL is
  // built at runtime so Vite serves the file as-is instead of bundling it.
  const base = import.meta.env.BASE_URL;
  const pyodideUrl = new URL(base + 'pyodide/pyodide.mjs', self.location.origin).href;
  const { loadPyodide } = await import(/* @vite-ignore */ pyodideUrl);
  py = await loadPyodide({ indexURL: base + 'pyodide/' });
  for (const f of PY_FILES) {
    const text = await (await fetch(base + 'py/' + f)).text();
    py.FS.writeFile(f, text);
  }
  py.runPython('import sys; sys.path.insert(0, ".")');
  py.runPython(GLUE);
}

const ready = init();

self.onmessage = async (e) => {
  const { id, cmd, args } = e.data;
  try {
    await ready;
    const fn = py.globals.get(cmd);
    const out = fn(...args);
    fn.destroy();
    self.postMessage({ id, result: JSON.parse(out) });
  } catch (err) {
    self.postMessage({ id, error: String(err) });
  }
};
