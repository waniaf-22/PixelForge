with open('PixelForge_Compiler.html', 'r', encoding='utf-8') as f:
    c = f.read()

replacements = {
    'â€”': '—',
    'Â·': '·',
    'â—€': '◀',
    'â–¶': '▶',
    'âœ¦': '✦',
    'âœ–': '✖',
    'âš ': '⚠',
    'â†³': '↳',
    'â ¸': '⏸',
    'â¬‡': '⬇',
    'âœ”': '✔',
    'â€“': '–',
    'â†‘': '↑',
    'â”€': '─'
}

for bad, good in replacements.items():
    c = c.replace(bad, good)

with open('PixelForge_Compiler.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done fixing mojibake.')
