
// ---------------------------------------------------------------------------
// Talking to the Python worker
// ---------------------------------------------------------------------------
const worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
let nextId = 0;
const pending = new Map();
worker.onmessage = (e) => {
  const { id, result, error } = e.data;
  const p = pending.get(id);
  pending.delete(id);
  if (error) p.reject(new Error(error));
  else p.resolve(result);
};
function call(cmd, ...args) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    worker.postMessage({ id, cmd, args });
  });
}

// ---------------------------------------------------------------------------
// Page elements
// ---------------------------------------------------------------------------
const $ = (id) => document.getElementById(id);
const boardEl = $('board');
const cells = [];
for (let i = 0; i < 16; i++) {
  const c = document.createElement('div');
  c.className = 'cell';
  boardEl.appendChild(c);
  cells.push(c);
}
const DIRS = ['up', 'down', 'left', 'right'];
const ARROWS = { up: '↑', down: '↓', left: '←', right: '→' };

let state = null;
let busy = false;       // a Python call is running
let playing = false;    // AI auto-play is on
let ready = false;

function setMessage(text) { $('message').textContent = text; }

function draw(s) {
  state = s;
  s.board.forEach((v, i) => {
    cells[i].textContent = v ? v : '';
    cells[i].className = 'cell' + (v ? ' t' + Math.min(v, 65536) : '');
    if (v >= 1024) cells[i].classList.add('small');
  });
  $('score').textContent = s.score.toLocaleString();
  $('maxtile').textContent = s.max_tile;
  $('moves').textContent = s.moves;
  if (s.over) setMessage('Game over! Final score ' + s.score.toLocaleString());
}

function drawBars(scores, best, time) {
  const legal = DIRS.filter((d) => scores[d] !== null);
  const vals = legal.map((d) => scores[d]);
  const lo = Math.min(...vals);
  const hi = Math.max(...vals);
  const bars = $('bars');
  bars.innerHTML = '';
  for (const d of DIRS) {
    const v = scores[d];
    const row = document.createElement('div');
    row.className = 'bar-row' + (d === best ? ' best' : '') + (v === null ? ' illegal' : '');
    const frac = v === null ? 0 : hi === lo ? 1 : 0.05 + 0.95 * (v - lo) / (hi - lo);
    const label = v === null ? 'illegal' : d === best ? 'best' : (v - hi).toFixed(0) + ' vs best';
    row.innerHTML =
      `<span class="dir">${ARROWS[d]} ${d}</span>` +
      `<span class="track"><span class="fill" style="width:${(frac * 100).toFixed(1)}%"></span></span>` +
      `<span class="val">${v === null ? '' : v.toFixed(1)}</span>` +
      `<span class="note">${label}</span>`;
    bars.appendChild(row);
  }
  const agent = $('agent').selectedOptions[0].textContent;
  $('ai-info').textContent = `${agent} chose ${ARROWS[best]} ${best} in ${(time * 1000).toFixed(0)} ms.`;
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------
async function newGame() {
  stopPlaying();
  if (!ready) return;
  draw(await call('new_game'));
  $('bars').innerHTML = '';
  $('ai-info').textContent = 'Press "AI: one move" to see the value of each direction.';
  setMessage('New game. Your move!');
}

async function humanMove(dir) {
  if (!ready || busy || playing || state.over) return;
  busy = true;
  const s = await call('human_move', dir);
  busy = false;
  draw(s);
  if (!s.over) setMessage(s.illegal ? `${dir} does not move anything` : `${dir}: +${s.gain} points`);
}

async function aiMove() {
  if (!ready || busy || state.over) return false;
  busy = true;
  const s = await call('ai_move', $('agent').value, Number($('depth').value),
    $('evalname').value, Number($('rollouts').value));
  busy = false;
  draw(s);
  if (s.best) drawBars(s.scores, s.best, s.time);
  if ($('stop2048').checked && s.max_tile >= 2048) {
    setMessage('Reached 2048! Score ' + s.score.toLocaleString());
    return false;
  }
  return !s.over;
}

function stopPlaying() {
  playing = false;
  $('btn-play').textContent = 'AI: play';
}

async function playLoop() {
  while (playing) {
    const more = await aiMove();
    if (!more) break;
    await new Promise((r) => setTimeout(r, Number($('delay').value)));
  }
  stopPlaying();
}

$('btn-new').onclick = () => newGame();
$('btn-step').onclick = () => { stopPlaying(); aiMove(); };
$('btn-play').onclick = () => {
  if (playing) { stopPlaying(); return; }
  playing = true;
  $('btn-play').textContent = 'AI: pause';
  setMessage('AI is playing...');
  playLoop();
};
$('delay').oninput = () => { $('delay-val').textContent = $('delay').value; };

const KEYS = {
  ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
  w: 'up', s: 'down', a: 'left', d: 'right', W: 'up', S: 'down', A: 'left', D: 'right',
};
window.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
  const dir = KEYS[e.key];
  if (dir) { e.preventDefault(); humanMove(dir); }
});

// Start: wait for Python to load, then open a new game.
call('new_game').then((s) => {
  ready = true;
  draw(s);
  setMessage('Ready. Play with the arrow keys, or let the AI play.');
}).catch((err) => setMessage('Could not load Python: ' + err.message));
