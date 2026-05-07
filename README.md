# ⚡ PixelForge Compiler

> **A Complete, Full-Stack, Browser-Based Compiler IDE for a custom Retro Pixel Art Domain-Specific Language (DSL).**
> 
> *Developed for CS4031 Compiler Construction.*

<div align="center">
  <img src="https://via.placeholder.com/800x450?text=PixelForge+IDE+Screenshot" alt="PixelForge IDE">
</div>

---

## 👥 Meet the Team
* **Minaal Fatima Jilani**
* **Wania Fatima**
* **Sameer Rajani**

---

## 📖 What is PixelForge?
PixelForge is not just a drawing tool; it is a **fully functional, 6-phase compiler** built from scratch. It reads custom code written in the "PixelForge DSL," analyzes it, optimizes it, and compiles it into Intermediate Representation (IR) instructions. These instructions are then executed by a custom Virtual Machine (VM) running entirely in your browser using HTML5 Canvas.

This project beautifully bridges low-level compiler theory (lexing, parsing, semantic checking) with a modern, cyberpunk-themed frontend UI.

---

## ⚙️ The 6-Phase Compiler Architecture

PixelForge strictly adheres to traditional compiler design principles. Here is exactly what happens under the hood when you hit **COMPILE**:

### Phase 1: Lexical Analysis (`lexer.py`)
The raw string of source code is ingested character by character.
* **Function**: Strips out whitespace and comments (`//`). Groups characters into meaningful chunks called **Tokens** using Regular Expressions.
* **Output**: A flat list of tokens (e.g., `T-CANVAS`, `T-IDENTIFIER`, `T-NUMBER(100)`). If an illegal character is found, it throws a `LexicalError`.

### Phase 2: Syntax Analysis (`parser.py`)
The token stream is fed into a **Recursive Descent Parser**.
* **Function**: Ensures the tokens appear in a grammatically correct order according to the DSL's rules. It builds a hierarchical **Abstract Syntax Tree (AST)**.
* **Output**: A tree of objects (e.g., `ProgramNode` containing a `CanvasNode` and multiple `DrawNode` children). Throws `SyntaxError` on violations (like missing arguments).

### Phase 3: Semantic Analysis (`semantic_analyzer.py`)
The compiler walks the AST to enforce the "meaning" and logic of the code.
* **Function**:
  1. Checks that `canvas` is declared first and only once.
  2. Ensures all coordinates and shapes fit within the bounds of the canvas.
  3. Verifies RGB color values fall precisely within the `0-255` range.
  4. Validates color names (e.g., "red", "cyan").
* **Output**: An annotated, verified AST. Throws `SemanticError` if logic is flawed.

### Phase 4: Intermediate Code Generation (`ir_generator.py`)
The complex AST hierarchy is flattened into linear, machine-readable instructions.
* **Function**: Generates **Three-Address Code (TAC)** style virtual machine instructions.
* **Output**: A JSON-serializable list of arrays. Example: `["DRAW_RECT", x, y, w, h]`, `["SET_COLOR", 255, 0, 0]`.

### Phase 5: Code Optimization (`optimizer.py`)
The flat IR is passed through several aggressive optimization passes to improve rendering speed.
* **Function**:
  1. **Dead Color Elimination**: Removes back-to-back color changes where the first color is never used to draw anything.
  2. **Duplicate Instruction Pruning**: Removes identical, consecutive draw commands.
  3. **Zero-Step Animation Removal**: Deletes `animate` commands that move by 0 steps.
  4. **Redundant Fill Collapse**: If the canvas is filled multiple times consecutively, only the last fill is kept.

### Phase 6: Target Code Execution (The Frontend Renderer)
The optimized IR is sent from the Python Flask Backend to the browser via REST API.
* **Function**: The JavaScript frontend parses the JSON IR and acts as the "Virtual Machine." It maps `DRAW` instructions to native HTML5 Canvas API calls and manages frame buffers for the `animate` commands.

---

## 🎨 The PixelForge DSL Specification

The language is whitespace-agnostic. Each command generally occupies a single line.

### 1. Canvas Setup
* **`canvas <width> <height>`**: Initializes the screen. Must be the first line.
  * *Example:* `canvas 400 400`
* **`fill <color>`**: Fills the entire canvas with the specified color.
  * *Example:* `fill black`

### 2. Color Management
* **`color <name>`**: Changes the active drawing color. Supported: `red`, `green`, `blue`, `cyan`, `magenta`, `yellow`, `white`, `black`, `gray`.
* **`color rgb(<r>, <g>, <b>)`**: Sets a custom color. Values must be 0-255.
  * *Example:* `color rgb(255, 128, 0)`

### 3. Drawing Geometry
*(Note: All shapes are drawn using the currently active color)*
* **`draw pixel <x> <y>`**: Paints a single pixel.
* **`draw square <x> <y> <size>`**: Draws a filled square starting from the top-left coordinate.
* **`draw rect <x> <y> <width> <height>`**: Draws a filled rectangle.
* **`draw circle <x> <y> <radius>`**: Draws a circle using the Bresenham Midpoint Algorithm.
* **`draw line <x1> <y1> <x2> <y2>`**: Draws a line connecting two points.
* **`draw triangle <x1> <y1> <x2> <y2> <x3> <y3>`**: Draws a filled triangle utilizing a custom scanline fill algorithm.

### 4. Animation
* **`animate move <direction> <steps>`**: Creates an animation sequence. It takes the current canvas state and shifts it pixel-by-pixel in the specified direction (`up`, `down`, `left`, `right`). Generates one frame per step.
  * *Example:* `animate move right 50`

---

## 💻 Example Program

Here is an example of what a PixelForge program looks like:

```text
// Initialize a 100x100 canvas
canvas 100 100
fill black

// Draw a red square
color red
draw square 10 10 20

// Draw a blue circle
color blue
draw circle 50 50 15

// Animate the entire scene moving downwards by 30 pixels
animate move down 30
```

---

## 📂 Complete Project Manifest

```text
PixelForge/
│
├── Compiler Core Modules (Python)
│   ├── lexer.py               # Phase 1: Regex-based Lexical Analyzer
│   ├── parser.py              # Phase 2: Recursive Descent Parser
│   ├── semantic_analyzer.py   # Phase 3: Context & Bounds Checker
│   ├── ir_generator.py        # Phase 4: AST to IR TAC Compiler
│   └── optimizer.py           # Phase 5: Peephole Optimizer
│
├── Web Architecture & IDE
│   ├── app.py                 # Flask REST API connecting Python to Web
│   ├── PixelForge_Compiler.html # The UI IDE and Target JS Virtual Machine
│   └── Language_Reference_Manual.txt # Complete formal specification of the DSL
│
└── Maintenance Scripts (Internal)
    ├── fix_utf8.py            # Converts source files to UTF-8
    ├── fix_utf8_bin.py        # Alternative UTF-8 encoding fixer
    ├── patch_minimize.py      # Injects UI window minimizing features
    ├── patch_samples.py       # Injects code samples into the IDE dropdown
    └── remove_src.py          # Utility script for source extraction
```

---

## ✨ Advanced IDE Features

* **Real-time Pipeline Visualization:** See exactly what each compiler phase is outputting live (Token Stream, AST, Semantic Errors, IR operations, Optimizer diffs).
* **Built-in Test Suite:** A dedicated tab containing 5 predefined test cases demonstrating semantic error handling, syntax error handling, dead-code elimination, Bresenham algorithms, and complex canvas rendering.
* **Fully Responsive UI:** The side-by-side cyberpunk interface intelligently scales and stacks on smaller screens, allowing seamless scrolling and editing anywhere.
* **Responsive Canvas Engine:** The HTML5 renderer automatically calculates pixel density and scales up or down based on your monitor size instantly, preserving crisp pixel art edges.

---

## 🚀 How to Install and Run Locally

Follow these exact steps to run the complete IDE on your local machine.

### Prerequisites
* **Python 3.8 or higher** installed.
* A modern web browser.

### 1. Clone the Source Code
```bash
git clone https://github.com/waniaf-22/PixelForge.git
cd PixelForge
```

### 2. Set Up a Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the Backend Requirements
The backend relies on Flask to serve the API.
```bash
pip install flask flask-cors
```

### 4. Boot the Compiler Server
Start the orchestrator API. Leave this terminal window open.
```bash
python app.py
```
*You should see output indicating the server is running on `http://127.0.0.1:5000`.*

### 5. Open the IDE
Open your web browser and navigate directly to the API endpoint. The Flask app will serve the HTML frontend.
* 👉 **Navigate to:** `http://127.0.0.1:5000/`

**You are now ready to write code, compile, and see the AST, IR, and rendering live!**

---
<div align="center">
  <i>"Compiling the retro future, pixel by pixel."</i>
</div>
