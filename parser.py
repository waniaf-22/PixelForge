"""
PixelForge Compiler — Phase 2: Syntax Analyzer (Parser)
CS4031 Compiler Construction · Spring 2026
Team: Minaal Fatima Jilani · Wania Fatima · Sameer Rajani

Consumes the token list produced by the Lexer and builds an
Abstract Syntax Tree (AST).

Grammar (LL(1)):
    program       → statement*
    statement     → canvas_stmt | color_stmt | fill_stmt
                  | draw_stmt  | animate_stmt
    canvas_stmt   → 'canvas' NUMBER NUMBER
    color_stmt    → 'color' color_value
    fill_stmt     → 'fill'  color_value
    color_value   → COLOR_NAME
                  | 'rgb' '(' NUMBER ',' NUMBER ',' NUMBER ')'
    draw_stmt     → 'draw' ( pixel_cmd | square_cmd | line_cmd )
    pixel_cmd     → 'pixel'  NUMBER NUMBER
    square_cmd    → 'square' NUMBER NUMBER NUMBER
    line_cmd      → 'line'   NUMBER NUMBER NUMBER NUMBER
    animate_stmt  → 'animate' 'move' DIRECTION NUMBER
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from lexer import Lexer, Token, LexerError


# ──────────────────────────────────────────────────────────────────────────────
#  AST node hierarchy
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ASTNode:
    line: int = field(default=0, repr=False)


@dataclass
class ColorValue:
    """Represents either a named colour or an rgb(r,g,b) value."""
    color_type: str          # "named" | "rgb"
    value: Optional[str] = None   # used when color_type == "named"
    r: Optional[int] = None
    g: Optional[int] = None
    b: Optional[int] = None

    def __repr__(self):
        if self.color_type == "named":
            return f"Color({self.value})"
        return f"Color(rgb({self.r},{self.g},{self.b}))"


@dataclass
class ProgramNode(ASTNode):
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class CanvasStmt(ASTNode):
    width: int = 0
    height: int = 0


@dataclass
class ColorStmt(ASTNode):
    color: ColorValue = field(default_factory=lambda: ColorValue("named", "white"))


@dataclass
class FillStmt(ASTNode):
    color: ColorValue = field(default_factory=lambda: ColorValue("named", "black"))


@dataclass
class DrawStmt(ASTNode):
    shape: str = ""          # "pixel" | "square" | "line" | "circle" | "rect" | "triangle"
    x: int = 0
    y: int = 0
    # square
    size: Optional[int] = None
    # rect
    w: Optional[int] = None
    h: Optional[int] = None
    # circle
    r: Optional[int] = None
    # line/triangle
    x2: Optional[int] = None
    y2: Optional[int] = None
    # triangle
    x3: Optional[int] = None
    y3: Optional[int] = None


@dataclass
class AnimateStmt(ASTNode):
    direction: str = ""      # "left" | "right" | "up" | "down"
    steps: int = 0


# ──────────────────────────────────────────────────────────────────────────────
#  ParseError
# ──────────────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    pass


# ──────────────────────────────────────────────────────────────────────────────
#  Parser
# ──────────────────────────────────────────────────────────────────────────────

class Parser:
    """
    Recursive-descent parser for PixelForge.

    Usage:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ── utilities ────────────────────────────────────────────────────────────

    def _cur(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self, offset: int = 1) -> Token:
        idx = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[idx]

    def _error(self, msg: str) -> ParseError:
        tok = self._cur()
        return ParseError(
            f"[Parser] {msg} (line {tok.line}, col {tok.col}) "
            f"— got {tok.type!r} ({tok.value!r})"
        )

    def _eat(self, expected_type: str) -> Token:
        tok = self._cur()
        if tok.type != expected_type:
            raise self._error(f"Expected {expected_type}")
        self.pos += 1
        return tok

    # ── public entry point ───────────────────────────────────────────────────

    def parse(self) -> ProgramNode:
        """Parse the full token stream and return a ProgramNode AST."""
        body = []
        while self._cur().type != "EOF":
            body.append(self._parse_stmt())
        return ProgramNode(body=body, line=1)

    # ── statement dispatch ───────────────────────────────────────────────────

    def _parse_stmt(self) -> ASTNode:
        tok = self._cur()
        dispatch = {
            "CANVAS":   self._parse_canvas,
            "COLOR":    self._parse_color,
            "FILL":     self._parse_fill,
            "DRAW":     self._parse_draw,
            "ANIMATE":  self._parse_animate,
        }
        handler = dispatch.get(tok.type)
        if handler is None:
            raise self._error(f"Unexpected token '{tok.value}' ({tok.type})")
        return handler()

    # ── canvas ───────────────────────────────────────────────────────────────

    def _parse_canvas(self) -> CanvasStmt:
        t = self._eat("CANVAS")
        w = self._eat("NUMBER")
        h = self._eat("NUMBER")
        return CanvasStmt(width=w.value, height=h.value, line=t.line)

    # ── colour helpers ───────────────────────────────────────────────────────

    def _parse_color_value(self) -> ColorValue:
        if self._cur().type == "COLOR_NAME":
            c = self._eat("COLOR_NAME")
            return ColorValue(color_type="named", value=c.value)
        if self._cur().type == "RGB":
            self._eat("RGB")
            self._eat("LPAREN")
            r = self._eat("NUMBER")
            self._eat("COMMA")
            g = self._eat("NUMBER")
            self._eat("COMMA")
            b = self._eat("NUMBER")
            self._eat("RPAREN")
            return ColorValue(color_type="rgb", r=r.value, g=g.value, b=b.value)
        raise self._error("Expected a colour name or rgb(R,G,B)")

    def _parse_color(self) -> ColorStmt:
        t = self._eat("COLOR")
        return ColorStmt(color=self._parse_color_value(), line=t.line)

    def _parse_fill(self) -> FillStmt:
        t = self._eat("FILL")
        return FillStmt(color=self._parse_color_value(), line=t.line)

    # ── draw ─────────────────────────────────────────────────────────────────

    def _parse_draw(self) -> DrawStmt:
        t = self._eat("DRAW")
        cmd = self._cur()

        if cmd.type == "PIXEL":
            self._eat("PIXEL")
            x = self._eat("NUMBER")
            y = self._eat("NUMBER")
            return DrawStmt(shape="pixel", x=x.value, y=y.value, line=t.line)

        if cmd.type == "SQUARE":
            self._eat("SQUARE")
            x = self._eat("NUMBER")
            y = self._eat("NUMBER")
            s = self._eat("NUMBER")
            return DrawStmt(shape="square", x=x.value, y=y.value, size=s.value, line=t.line)

        if cmd.type == "LINE":
            self._eat("LINE")
            x1 = self._eat("NUMBER")
            y1 = self._eat("NUMBER")
            x2 = self._eat("NUMBER")
            y2 = self._eat("NUMBER")
            return DrawStmt(
                shape="line",
                x=x1.value, y=y1.value,
                x2=x2.value, y2=y2.value,
                line=t.line
            )

        if cmd.type == "CIRCLE":
            self._eat("CIRCLE")
            cx = self._eat("NUMBER")
            cy = self._eat("NUMBER")
            r = self._eat("NUMBER")
            return DrawStmt(shape="circle", x=cx.value, y=cy.value, r=r.value, line=t.line)

        if cmd.type == "RECT":
            self._eat("RECT")
            rx = self._eat("NUMBER")
            ry = self._eat("NUMBER")
            w = self._eat("NUMBER")
            h = self._eat("NUMBER")
            return DrawStmt(shape="rect", x=rx.value, y=ry.value, w=w.value, h=h.value, line=t.line)

        if cmd.type == "TRIANGLE":
            self._eat("TRIANGLE")
            x1 = self._eat("NUMBER")
            y1 = self._eat("NUMBER")
            x2 = self._eat("NUMBER")
            y2 = self._eat("NUMBER")
            x3 = self._eat("NUMBER")
            y3 = self._eat("NUMBER")
            return DrawStmt(
                shape="triangle",
                x=x1.value, y=y1.value,
                x2=x2.value, y2=y2.value,
                x3=x3.value, y3=y3.value,
                line=t.line
            )

        raise self._error(f"Unknown draw command '{cmd.value}'")

    # ── animate ──────────────────────────────────────────────────────────────

    def _parse_animate(self) -> AnimateStmt:
        t = self._eat("ANIMATE")
        self._eat("MOVE")
        d = self._eat("DIRECTION")
        n = self._eat("NUMBER")
        return AnimateStmt(direction=d.value, steps=n.value, line=t.line)


# ──────────────────────────────────────────────────────────────────────────────
#  Pretty-printer for the AST
# ──────────────────────────────────────────────────────────────────────────────

def pretty_print_ast(node: ASTNode, indent: int = 0) -> str:
    pad = "  " * indent
    lines = []

    if isinstance(node, ProgramNode):
        lines.append(f"{pad}Program ({len(node.body)} statements)")
        for child in node.body:
            lines.append(pretty_print_ast(child, indent + 1))

    elif isinstance(node, CanvasStmt):
        lines.append(f"{pad}CanvasStmt  width={node.width}  height={node.height}  [L{node.line}]")

    elif isinstance(node, ColorStmt):
        lines.append(f"{pad}ColorStmt   color={node.color}  [L{node.line}]")

    elif isinstance(node, FillStmt):
        lines.append(f"{pad}FillStmt    color={node.color}  [L{node.line}]")

    elif isinstance(node, DrawStmt):
        extra = ""
        if node.shape == "pixel":
            extra = f"x={node.x} y={node.y}"
        elif node.shape == "square":
            extra = f"x={node.x} y={node.y} size={node.size}"
        elif node.shape == "line":
            extra = f"({node.x},{node.y})→({node.x2},{node.y2})"
        lines.append(f"{pad}DrawStmt    shape={node.shape}  {extra}  [L{node.line}]")

    elif isinstance(node, AnimateStmt):
        lines.append(f"{pad}AnimateStmt dir={node.direction}  steps={node.steps}  [L{node.line}]")

    else:
        lines.append(f"{pad}{node!r}")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
#  CLI helper
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    src = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    try:
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        print(pretty_print_ast(ast))
    except (LexerError, ParseError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
