import sys

with open('PixelForge_Compiler.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add minimized-debug CSS
css_to_add = """
/* ── Minimize Debug Col ── */
.main.minimized-debug {
  grid-template-rows: 1fr auto !important;
}
.main.minimized-debug .debug-col {
  border-top: none;
}
.main.minimized-debug .tc, 
.main.minimized-debug #tc-pipeline, 
.main.minimized-debug #tc-source {
  display: none !important;
}
.tab-row button.tab-minimize {
  margin-left: auto;
  color: var(--dim);
}
.tab-row button.tab-minimize:hover {
  color: var(--bright);
}
"""

if '/* ── Minimize Debug Col ── */' not in c:
    c = c.replace('/* ── Panel Header ── */', css_to_add + '\n/* ── Panel Header ── */')

# 2. Add the toggle button in HTML
html_to_replace = """    <div class="tab-row">
      <button class="tab on" id="tab-pipeline" onclick="switchTab(this,'pipeline')">PIPELINE</button>
      <button class="tab" onclick="switchTab(this,'source');loadSourceCode()">SOURCE</button>
      <button class="tab" onclick="switchTab(this,'ref')">LANG REF</button>
    </div>"""

html_replacement = """    <div class="tab-row">
      <button class="tab on" id="tab-pipeline" onclick="switchTab(this,'pipeline')">PIPELINE</button>
      <button class="tab" onclick="switchTab(this,'source');loadSourceCode()">SOURCE</button>
      <button class="tab" onclick="switchTab(this,'ref')">LANG REF</button>
      <button class="tab tab-minimize" id="toggle-debug-btn" onclick="toggleDebugPanel()">▲ EXPAND</button>
    </div>"""

if 'id="toggle-debug-btn"' not in c:
    c = c.replace(html_to_replace, html_replacement)

# 3. Add the main div starting minimized
if '<div class="main">' in c:
    c = c.replace('<div class="main">', '<div class="main minimized-debug">')

# 4. Add the JS functions
js_to_add = """
function toggleDebugPanel() {
  const main = document.querySelector('.main');
  const btn = document.getElementById('toggle-debug-btn');
  main.classList.toggle('minimized-debug');
  if (main.classList.contains('minimized-debug')) {
    btn.textContent = '▲ EXPAND';
  } else {
    btn.textContent = '▼ MINIMIZE';
  }
}
function expandDebugPanel() {
  const main = document.querySelector('.main');
  main.classList.remove('minimized-debug');
  const btn = document.getElementById('toggle-debug-btn');
  if(btn) btn.textContent = '▼ MINIMIZE';
}
"""

if 'function expandDebugPanel()' not in c:
    # Insert at the top of the script tag
    c = c.replace('let USE_BACKEND = true;', js_to_add + '\nlet USE_BACKEND = true;')

# 5. Call expandDebugPanel() inside compile()
if 'expandDebugPanel();' not in c:
    # Find async function compile() {
    c = c.replace('async function compile() {', 'async function compile() {\n  expandDebugPanel();')

with open('PixelForge_Compiler.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Minimize features added.')
