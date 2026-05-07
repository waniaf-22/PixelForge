"""
PixelForge Compiler — Phase 4: IR Generator (Intermediate Representation)
CS4031 Compiler Construction · Spring 2026
Team: Minaal Fatima Jilani · Wania Fatima · Sameer Rajani

Converts the validated AST into a flat list of low-level, three-address-style
IR instructions. The IR completely decouples the front-end (lexing / parsing /
semantic analysis) from the back-end (code optimisation and code generation).

IR opcode set:
    INIT_CANVAS      W H
    SET_COLOR        name
    SET_COLOR_RGB    R G B
    FILL_CANVAS      name
    FILL_CANVAS_RGB  R G B
    DRAW_PIXEL       X Y
    DRAW_SQUARE      X Y Size
    DRAW_LINE        X1 Y1 X2 Y2
    ANIMATE_MOVE     direction steps
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List

from lexer import Lexer, LexerError
from parser import (
    Parser, ParseError,
    ProgramNode, CanvasStmt, ColorStmt, FillStmt, DrawStmt, AnimateStmt,
    ASTNode
)


# ──────────────────────────────────────────────────────────────────────────────
#  IR Instruction
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class IRInstruction:
    op: str
    args: List[Any] = field(default_factory=list)

    def __repr__(self):
        args_str = "  ".join(str(a) for a in self.args)
        return f"{self.op:<20} {args_str}"


# ──────────────────────────────────────────────────────────────────────────────
#  IRGen
# ──────────────────────────────────────────────────────────────────────────────

class IRGen:
    """
    Generates a flat IR instruction list from a PixelForge ProgramNode AST.

    Usage:
        ir = IRGen().generate(ast)
        for instr in ir:
            print(instr)
    """

    def generate(self, ast: ProgramNode) -> List[IRInstruction]:
        ir: List[IRInstruction] = []
        for node in ast.body:
            self._emit(node, ir)
        return ir

    def _emit(self, node: ASTNode, ir: List[IRInstruction]):
        if isinstance(node, CanvasStmt):
            ir.append(IRInstruction("INIT_CANVAS", [node.width, node.height]))

        elif isinstance(node, ColorStmt):
            cv = node.color
            if cv.color_type == "named":
                ir.append(IRInstruction("SET_COLOR", [cv.value]))
            else:
                ir.append(IRInstruction("SET_COLOR_RGB", [cv.r, cv.g, cv.b]))

        elif isinstance(node, FillStmt):
            cv = node.color
            if cv.color_type == "named":
                ir.append(IRInstruction("FILL_CANVAS", [cv.value]))
            else:
                ir.append(IRInstruction("FILL_CANVAS_RGB", [cv.r, cv.g, cv.b]))

        elif isinstance(node, DrawStmt):
            if node.shape == "pixel":
                ir.append(IRInstruction("DRAW_PIXEL", [node.x, node.y]))
            elif node.shape == "square":
                ir.append(IRInstruction("DRAW_SQUARE", [node.x, node.y, node.size]))
            elif node.shape == "line":
                ir.append(IRInstruction("DRAW_LINE", [node.x, node.y, node.x2, node.y2]))
            elif node.shape == "circle":
                ir.append(IRInstruction("DRAW_CIRCLE", [node.x, node.y, node.r]))
            elif node.shape == "rect":
                ir.append(IRInstruction("DRAW_RECT", [node.x, node.y, node.w, node.h]))
            elif node.shape == "triangle":
                ir.append(IRInstruction("DRAW_TRIANGLE", [node.x, node.y, node.x2, node.y2, node.x3, node.y3]))

        elif isinstance(node, AnimateStmt):
            ir.append(IRInstruction("ANIMATE_MOVE", [node.direction, node.steps]))


# ──────────────────────────────────────────────────────────────────────────────
#  Pretty-printer
# ──────────────────────────────────────────────────────────────────────────────

def dump_ir(ir: List[IRInstruction]) -> str:
    lines = [f"{'IDX':<5} {'OPCODE':<22} ARGS"]
    lines.append("─" * 55)
    for i, instr in enumerate(ir):
        lines.append(f"{i:<5} {instr!r}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
#  CLI helper
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    src = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    try:
        tokens = Lexer(src).tokenize()
        ast    = Parser(tokens).parse()
        ir     = IRGen().generate(ast)
        print(dump_ir(ir))
    except (LexerError, ParseError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
