// Runs before `npm run dev`: copies the Python AI files and the Pyodide runtime
// into public/ so the browser can load them (works offline, no server needed).
import { cpSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const pyDir = join(here, 'public', 'py');
mkdirSync(pyDir, { recursive: true });
for (const f of ['game.py', 'heuristics.py', 'agents.py']) {
  cpSync(join(here, '..', f), join(pyDir, f));
}

const pyodideSrc = join(here, 'node_modules', 'pyodide');
if (!existsSync(pyodideSrc)) {
  console.error('Pyodide not installed. Run "npm install" first.');
  process.exit(1);
}
cpSync(pyodideSrc, join(here, 'public', 'pyodide'), { recursive: true });
console.log('Copied game.py, heuristics.py, agents.py and Pyodide into public/');
