import re
with open('PixelForge_Compiler.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Remove all occurrences of the SRC button
c = re.sub(r'<button class="src-btn".*?>SRC</button>\n?', '', c)

with open('PixelForge_Compiler.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('SRC buttons removed.')
