"""
PixelForge Compiler — Phase 3: Semantic Analyzer
CS4031 Compiler Construction · Spring 2026
Team: Minaal Fatima Jilani · Wania Fatima · Sameer Rajani

Walks the AST and validates logical / type correctness.

Checks performed:
  • Canvas must be defined before any draw / animate / fill
  • Canvas dimensions must be positive and ≤ 256×256
  • Canvas may not be redefined (warning)
  • RGB component values must be 0–255
  • Drawing without setting a colour (warning, defaults to white)
  • Pixel coordinates must be within canvas bounds
  • Square size must be positive; position must be non-negative
  • Square that clips canvas edge  → warning
  • Line endpoints outside canvas  → warning
  • Animation steps must be positive; >64 steps → performance warning
  • Color/fill before canvas is defined → warning
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple

from lexer import Lexer, LexerError
from parser import (
    Parser, ParseError,
    ProgramNode, CanvasStmt, ColorStmt, FillStmt, DrawStmt, AnimateStmt,
    ASTNode
)


# ──────────────────────────────────────────────────────────────────────────────
#  Diagnostic dataclasses
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SemanticError:
    message: str
    line: int

    def __str__(self):
        return f"[SemanticError] L{self.line}: {self.message}"


@dataclass
class SemanticWarning:
    message: str
    line: int

    def __str__(self):
        return f"[SemanticWarning] L{self.line}: {self.message}"


@dataclass
class SemanticResult:
    errors: List[SemanticError] = field(default_factory=list)
    warnings: List[SemanticWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        for w in self.warnings:
            lines.append(str(w))
        for e in self.errors:
            lines.append(str(e))
        if not lines:
            lines.append("[Semantic] Analysis passed — no errors or warnings.")
        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
#  SemanticAnalyzer
# ──────────────────────────────────────────────────────────────────────────────

class SemanticAnalyzer:
    """
    Performs semantic analysis on a PixelForge AST.

    Usage:
        result = SemanticAnalyzer(ast).analyze()
        if not result.ok:
            print(result.summary())
    """

    MAX_W = 256
    MAX_H = 256
    WARN_STEPS = 64

    def __init__(self, ast: ProgramNode):
        self.ast = ast
        self._result = SemanticResult()
        # Symbol-table / state
        self._canvas_defined = False
        self._color_set = False
        self._canvas_w = 0
        self._canvas_h = 0

    # ── public ───────────────────────────────────────────────────────────────

    def analyze(self) -> SemanticResult:
        for node in self.ast.body:
            self._check(node)
        return self._result

    # ── internal helpers ─────────────────────────────────────────────────────

    def _err(self, msg: str, line: int):
        self._result.errors.append(SemanticError(msg, line))

    def _warn(self, msg: str, line: int):
        self._result.warnings.append(SemanticWarning(msg, line))

    def _check(self, node: ASTNode):
        if isinstance(node, CanvasStmt):
            self._check_canvas(node)
        elif isinstance(node, (ColorStmt, FillStmt)):
            self._check_color_or_fill(node)
        elif isinstance(node, DrawStmt):
            self._check_draw(node)
        elif isinstance(node, AnimateStmt):
            self._check_animate(node)

    # ── per-node checks ───────────────────────────────────────────────────────

    def _check_canvas(self, node: CanvasStmt):
        if self._canvas_defined:
            self._warn("Canvas redefinition — previous canvas replaced.", node.line)

        if node.width <= 0 or node.height <= 0:
            self._err(
                f"Canvas dimensions must be positive, got {node.width}×{node.height}.",
                node.line
            )
        elif node.width > self.MAX_W or node.height > self.MAX_H:
            self._err(
                f"Canvas too large — maximum is {self.MAX_W}×{self.MAX_H}, "
                f"got {node.width}×{node.height}.",
                node.line
            )

        self._canvas_w = node.width
        self._canvas_h = node.height
        self._canvas_defined = True

    def _check_color_or_fill(self, node):
        if not self._canvas_defined:
            self._warn("Color/fill set before canvas is defined.", node.line)

        cv = node.color
        if cv.color_type == "rgb":
            for component, name in [(cv.r, "R"), (cv.g, "G"), (cv.b, "B")]:
                if not (0 <= component <= 255):
                    self._err(
                        f"RGB channel {name}={component} out of range (0–255).",
                        node.line
                    )
        self._color_set = True

    def _check_draw(self, node: DrawStmt):
        if not self._canvas_defined:
            self._err("Must define a canvas before drawing.", node.line)
            return

        if not self._color_set:
            self._warn(
                "Drawing without setting a colour — defaults to white.",
                node.line
            )

        W, H = self._canvas_w, self._canvas_h

        if node.shape == "pixel":
            if not (0 <= node.x < W and 0 <= node.y < H):
                self._err(
                    f"Pixel ({node.x},{node.y}) is out of bounds for "
                    f"{W}×{H} canvas.",
                    node.line
                )

        elif node.shape == "square":
            if node.size is None or node.size <= 0:
                self._err("Square size must be a positive integer.", node.line)
            if node.x < 0 or node.y < 0:
                self._err(
                    f"Square position ({node.x},{node.y}) cannot be negative.",
                    node.line
                )
            if node.size and (node.x + node.size > W or node.y + node.size > H):
                self._warn(
                    f"Square at ({node.x},{node.y}) with size {node.size} "
                    f"clips the canvas edge ({W}×{H}).",
                    node.line
                )

        elif node.shape == "line":
            endpoints: List[Tuple[int, int]] = [(node.x, node.y), (node.x2, node.y2)]
            for (ex, ey) in endpoints:
                if not (0 <= ex < W and 0 <= ey < H):
                    self._warn(
                        f"Line endpoint ({ex},{ey}) is outside the canvas bounds.",
                        node.line
                    )

    def _check_animate(self, node: AnimateStmt):
        if not self._canvas_defined:
            self._err("Must define a canvas before animating.", node.line)

        if node.steps <= 0:
            self._err(
                f"Animation steps must be a positive integer, got {node.steps}.",
                node.line
            )
        elif node.steps > self.WARN_STEPS:
            self._warn(
                f"{node.steps} animation steps may be slow to render "
                f"(warning threshold: {self.WARN_STEPS}).",
                node.line
            )


# ──────────────────────────────────────────────────────────────────────────────
#  CLI helper
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    src = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    try:
        tokens = Lexer(src).tokenize()
        ast    = Parser(tokens).parse()
        result = SemanticAnalyzer(ast).analyze()
        print(result.summary())
        sys.exit(0 if result.ok else 1)
    except (LexerError, ParseError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
