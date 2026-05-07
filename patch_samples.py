import re

with open('PixelForge_Compiler.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Remove the Shapes and Triangles buttons
c = re.sub(r'\s*<button class="chip"[^>]*>Shapes</button>', '', c)
c = re.sub(r'\s*<button class="chip"[^>]*>Triangles</button>', '', c)

# 2. Add animation to smiley
smiley_original = """draw square 13 16 1
draw square 14 15 1`,"""
smiley_new = """draw square 13 16 1
draw square 14 15 1
animate move up 6`,"""
c = c.replace(smiley_original, smiley_new)

# 3. Add animation to rainbow
rainbow_original = """draw square 0 18 24
draw square 0 19 24`,"""
rainbow_new = """draw square 0 18 24
draw square 0 19 24
animate move left 12`,"""
c = c.replace(rainbow_original, rainbow_new)

with open('PixelForge_Compiler.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Modifications applied.')
