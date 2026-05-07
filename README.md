# PixelForge Compiler ⚡

A browser-based Compiler Design IDE for a custom Retro Pixel Art Domain-Specific Language (DSL). Developed for **CS4031 Compiler Construction**.

### 👥 Team
* Minaal Fatima Jilani
* Wania Fatima
* Sameer Rajani

---

## 📂 Project Structure

```text
PixelForge/
├── app.py                     # Flask Server & Compilation Orchestrator
├── PixelForge_Compiler.html   # IDE Frontend Interface & Target VM
│
├── Compiler Modules/
│   ├── lexer.py               # Phase 1: Lexical Analysis
│   ├── parser.py              # Phase 2: Syntax Analysis (AST)
│   ├── semantic_analyzer.py   # Phase 3: Semantic Analysis
│   ├── ir_generator.py        # Phase 4: Intermediate Representation
│   └── optimizer.py           # Phase 5: Code Optimization
│
└── Scripts/
    ├── fix_utf8.py            # Encoding utility
    └── patch_minimize.py      # UI patching utility
```

---

## 🚀 Quick Start

1. **Install Dependencies**
   Ensure you have Python installed, then run:
   ```bash
   pip install flask flask-cors
   ```

2. **Run the Compiler Server**
   Start the backend in your terminal:
   ```bash
   python app.py
   ```

3. **Open the IDE**
   Open your web browser and go to:
   ```text
   http://127.0.0.1:5000/
   ```

---

## ⚙️ How It Works

PixelForge strictly implements a 6-phase compiler pipeline:
1. **Lexer:** Converts raw source code into structured Tokens.
2. **Parser:** Builds an Abstract Syntax Tree (AST) from the tokens.
3. **Semantic Analyzer:** Checks for contextual and logical errors (e.g., drawing out of bounds).
4. **IR Generator:** Flattens the AST down into Three-Address Code (TAC).
5. **Optimizer:** Removes dead code, redundant fills, duplicate calls, and zero-step animations.
6. **Frontend Renderer:** The browser acts as the target VM, interpreting the optimized IR to paint pixels on the HTML5 canvas.

---

## 🎨 Language Syntax

**Setup & Colors**
* `canvas W H` - Initialize canvas width and height (Must be first)
* `fill COLOR` - Fill background
* `color NAME` or `color rgb(R,G,B)` - Set pen color

**Drawing**
* `draw pixel X Y`
* `draw square X Y SIZE`
* `draw rect X Y W H`
* `draw circle X Y R`
* `draw line X1 Y1 X2 Y2`
* `draw triangle X1 Y1 X2 Y2 X3 Y3`

**Animation**
* `animate move DIR N` - Moves all shapes `up`, `down`, `left`, or `right` by `N` steps, generating frames.
