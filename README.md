# PixelForge Compiler ⚡

**A full-stack, browser-based Compiler Design IDE for a custom Retro Pixel Art Domain-Specific Language (DSL).**

Developed for **CS4031 Compiler Construction · Spring 2026**.

## 👥 Team
* **Minaal Fatima Jilani**
* **Wania Fatima**
* **Sameer Rajani**

---

## 📖 Overview
PixelForge is a complete, 6-phase compiler built to parse, analyze, and generate animated pixel art directly from a custom Domain-Specific Language (DSL). It consists of two main parts:
1. **The Python Backend Server (`app.py`)**: A Flask-based API that strictly implements the formal phases of a compiler.
2. **The IDE Frontend (`PixelForge_Compiler.html`)**: A cyberpunk/clean-tech styled browser interface that allows you to write code, compile it, and view the output of *every* compiler phase in real-time, alongside a live pixel art canvas.

## ✨ Features
* **Custom DSL**: Simple syntax for drawing pixels, squares, rectangles, circles, lines, and animating them.
* **Full 6-Phase Compiler Pipeline**: Watch your source code transform in real-time.
* **Intelligent Optimiser**: Eliminates dead code, duplicate draws, and unreachable animations (zero-step moves).
* **Live Pixel Canvas**: See your code rendered visually on an HTML5 canvas.
* **Animation Support**: Render multiple frames and play them back at varying FPS using the `animate` command.
* **Integrated Source Viewer**: Read the compiler's own Python source code natively within the IDE.

---

## ⚙️ Architecture & The 6-Phase Pipeline

PixelForge rigidly implements standard compiler construction principles:

### 1. Lexical Analysis (`lexer.py`)
Reads the raw source code string and converts it into a stream of **Tokens** (e.g., `T-CANVAS`, `T-IDENTIFIER`, `T-NUMBER`). Strips out comments and whitespace, and strictly validates that no illegal characters enter the pipeline.

### 2. Syntax Analysis (`parser.py`)
Consumes the token stream and builds an **Abstract Syntax Tree (AST)** using a Recursive Descent parsing strategy. Enforces the grammar rules (e.g., ensuring `canvas` is declared properly, shapes receive the correct number of numeric arguments).

### 3. Semantic Analysis (`semantic_analyzer.py`)
Traverses the AST to check for logical and contextual errors. 
* *Errors*: Out-of-bounds drawing, drawing before canvas initialization, invalid RGB ranges (must be 0-255).
* *Warnings*: Redundant canvas definitions.

### 4. Intermediate Code Generation (`ir_generator.py`)
Converts the AST into flat, linear **Three-Address Code (TAC) / Intermediate Representation (IR)**. This breaks complex statements down into elementary virtual machine instructions like `INIT_CANVAS`, `SET_COLOR`, and `DRAW_PIXEL`.

### 5. Code Optimization (`optimizer.py`)
Applies a series of optimization passes over the flat IR list to make the final output more efficient:
* **Dead-color elimination**: Removes consecutive color assignments where the first color is never used.
* **Redundant fill collapse**: Collapses multiple canvas fills into a single operation.
* **Out-of-bounds pruning**: Discards `DRAW` instructions that are mathematically proven to fall outside the canvas boundaries.
* **Zero-step animate removal**: Eliminates animations that move by 0 steps.
* **Duplicate-draw elimination**: Removes completely identical drawing operations that occur consecutively.

### 6. Target Code Generation (Frontend JS Renderer)
The optimized IR is sent back to the browser via the Flask API. The frontend acts as the "VM", interpreting the IR instructions to paint colored pixels to the internal canvas state and manage animation frames.

---

## 🎨 PixelForge DSL Reference

### Setup
* `canvas W H`: Defines the width and height of the pixel canvas (Must be the first command).
* `fill COLOR`: Flood-fills the background.

### Colors
* `color NAME`: Sets the pen color (e.g., `red`, `green`, `blue`, `cyan`, `magenta`, `yellow`, `white`, `black`, `gray`).
* `color rgb(R,G,B)`: Sets a precise custom color.

### Shapes
* `draw pixel X Y`: Draw a single dot.
* `draw square X Y SIZE`: Draw a filled square.
* `draw rect X Y W H`: Draw a filled rectangle.
* `draw circle X Y R`: Draw a circle using the Bresenham midpoint algorithm.
* `draw line X1 Y1 X2 Y2`: Draw a line using Bresenham's line algorithm.
* `draw triangle X1 Y1 X2 Y2 X3 Y3`: Draw a filled triangle using a scanline fill algorithm.

### Animation
* `animate move DIR N`: Animates all previously drawn shapes by shifting them in `DIR` (`up`, `down`, `left`, `right`) for `N` steps. This generates an animation frame per step.

---

## 🚀 How to Run

1. **Install Dependencies**
   Ensure you have Python installed, then install Flask:
   ```bash
   pip install flask flask-cors
   ```

2. **Start the Backend Compiler Server**
   Run the Flask API in the project directory:
   ```bash
   python app.py
   ```
   *The server will start listening on `http://127.0.0.1:5000`.*

3. **Open the IDE**
   Because Flask is configured to serve the root endpoint, simply open your web browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

4. **Write and Compile**
   * Write code in the Source Code Editor or click on one of the **Samples** (`Basic`, `Smiley`, `Spaceship`, `Rainbow`, `Logo`).
   * Click **⚡ COMPILE & RUN**.
   * Click **▲ EXPAND** on the bottom right to open the Pipeline Debugger and view the outputs generated by the Lexer, Parser, IR Gen, and Optimizer.

---

## 🛠️ Tech Stack
* **Backend**: Python 3, Flask, Flask-CORS
* **Frontend**: HTML5 Canvas, Vanilla CSS3 (Custom Grid/Flexbox Layouts), Vanilla JavaScript
* **Theme**: Custom Retro Cyberpunk/Clean-Tech Dark Mode with CRT effects.
