"""
PixelForge Compiler — Phase 5: Code Optimizer
CS4031 Compiler Construction · Spring 2026
Team: Minaal Fatima Jilani · Wania Fatima · Sameer Rajani

Applies a series of optimisation passes over the flat IR list.

Optimisation passes implemented
────────────────────────────────
1.  Dead-colour elimination
    Consecutive SET_COLOR / SET_COLOR_RGB instructions where only the last
    one is actually followed by a draw command are removed.

2.  Redundant INIT_CANVAS elimination
    If INIT_CANVAS is called more than once, only the last definition
    is kept (the semantic analyser already warns about this).

3.  Redundant FILL_CANVAS elimination
    Consecutive FILL_CANVAS / FILL_CANVAS_RGB instructions where only the
    last one matters are collapsed.

4.  Constant-fold zero-step animations
    ANIMATE_MOVE with steps == 0 is removed (unreachable code).

5.  Out-of-bounds draw pruning
    DRAW_PIXEL instructions that reference coordinates outside the canvas
    are removed and reported as optimiser notes.

6.  Duplicate-draw elimination
    Consecutive identical DRAW_PIXEL instructions at the same coordinates
    and colour are deduplicated.

Each pass is independent and re-runnable; the optimizer reports what it did.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

from lexer import Lexer, LexerError
from parser import Parser, ParseError
from ir_generator import IRGen, IRInstruction, dump_ir


# ──────────────────────────────────────────────────────────────────────────────
#  Optimiser result
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class OptimiserResult:
    ir: List[IRInstruction]
    notes: List[str] = field(default_factory=list)
    removed: int = 0

    def summary(self) -> str:
        lines = [f"[Optimiser] {self.removed} instruction(s) eliminated."]
        for note in self.notes:
            lines.append(f"  ↳ {note}")
        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
#  Optimizer
# ──────────────────────────────────────────────────────────────────────────────

class Optimizer:
    """
    Multi-pass IR optimizer for PixelForge.

    Usage:
        result = Optimizer(ir).optimize()
        optimised_ir = result.ir
        print(result.summary())
    """

    _COLOR_OPS      = {"SET_COLOR", "SET_COLOR_RGB"}
    _FILL_OPS       = {"FILL_CANVAS", "FILL_CANVAS_RGB"}
    _DRAW_OPS       = {"DRAW_PIXEL", "DRAW_SQUARE", "DRAW_LINE", "DRAW_CIRCLE", "DRAW_RECT", "DRAW_TRIANGLE"}
    _CANVAS_OP      = "INIT_CANVAS"
    _ANIMATE_OP     = "ANIMATE_MOVE"

    def __init__(self, ir: List[IRInstruction]):
        self._ir = [IRInstruction(i.op, list(i.args)) for i in ir]   # deep copy
        self._notes: List[str] = []
        self._removed = 0

    def optimize(self) -> OptimiserResult:
        self._pass_redundant_canvas()
        self._pass_dead_color()
        self._pass_redundant_fill()
        self._pass_zero_step_animate()
        self._pass_oob_draw_prune()
        self._pass_duplicate_draw()
        return OptimiserResult(ir=self._ir, notes=self._notes, removed=self._removed)

    # ── internal ─────────────────────────────────────────────────────────────

    def _note(self, msg: str, count: int = 1):
        self._notes.append(msg)
        self._removed += count

    def _canvas_size(self) -> Tuple[int, int]:
        """Return (W, H) from the last INIT_CANVAS in the current IR."""
        for instr in reversed(self._ir):
            if instr.op == self._CANVAS_OP:
                return instr.args[0], instr.args[1]
        return 0, 0

    # Pass 1 — keep only the last INIT_CANVAS ────────────────────────────────

    def _pass_redundant_canvas(self):
        canvas_indices = [i for i, ins in enumerate(self._ir)
                          if ins.op == self._CANVAS_OP]
        if len(canvas_indices) <= 1:
            return
        to_remove = set(canvas_indices[:-1])
        removed = len(to_remove)
        self._ir = [ins for i, ins in enumerate(self._ir) if i not in to_remove]
        self._note(f"Removed {removed} redundant INIT_CANVAS instruction(s).", removed)

    # Pass 2 — dead colour elimination ────────────────────────────────────────

    def _pass_dead_color(self):
        """
        A SET_COLOR / SET_COLOR_RGB is 'dead' if it is followed by another
        colour-set instruction before any draw instruction that would use it.
        """
        new_ir: List[IRInstruction] = []
        removed = 0
        i = 0
        while i < len(self._ir):
            ins = self._ir[i]
            if ins.op in self._COLOR_OPS:
                # Look ahead: is this colour used before the next SET_COLOR?
                j = i + 1
                used = False
                while j < len(self._ir):
                    nxt = self._ir[j]
                    if nxt.op in self._DRAW_OPS:
                        used = True
                        break
                    if nxt.op in self._COLOR_OPS:
                        break   # overwritten — not used
                    j += 1
                if not used:
                    removed += 1
                    i += 1
                    continue
            new_ir.append(ins)
            i += 1

        if removed:
            self._note(f"Eliminated {removed} dead SET_COLOR instruction(s).", removed)
        self._ir = new_ir

    # Pass 3 — redundant fill collapse ───────────────────────────────────────

    def _pass_redundant_fill(self):
        """Keep only the last consecutive FILL_CANVAS before draw commands."""
        new_ir: List[IRInstruction] = []
        removed = 0
        i = 0
        while i < len(self._ir):
            ins = self._ir[i]
            if ins.op in self._FILL_OPS:
                # Check if next meaningful instruction is also a fill
                j = i + 1
                if j < len(self._ir) and self._ir[j].op in self._FILL_OPS:
                    removed += 1
                    i += 1
                    continue
            new_ir.append(ins)
            i += 1

        if removed:
            self._note(f"Collapsed {removed} redundant FILL_CANVAS instruction(s).", removed)
        self._ir = new_ir

    # Pass 4 — zero-step animate removal ─────────────────────────────────────

    def _pass_zero_step_animate(self):
        before = len(self._ir)
        self._ir = [ins for ins in self._ir
                    if not (ins.op == self._ANIMATE_OP and ins.args[1] == 0)]
        removed = before - len(self._ir)
        if removed:
            self._note(f"Removed {removed} zero-step ANIMATE_MOVE instruction(s).", removed)

    # Pass 5 — out-of-bounds pixel pruning ───────────────────────────────────

    def _pass_oob_draw_prune(self):
        W, H = self._canvas_size()
        if W == 0 or H == 0:
            return
        new_ir: List[IRInstruction] = []
        removed = 0
        for ins in self._ir:
            if ins.op == "DRAW_PIXEL":
                x, y = ins.args[0], ins.args[1]
                if not (0 <= x < W and 0 <= y < H):
                    self._note(
                        f"Pruned out-of-bounds DRAW_PIXEL({x},{y}) "
                        f"for canvas {W}×{H}."
                    )
                    removed += 1
                    continue
            new_ir.append(ins)
        self._ir = new_ir
        if removed:
            self._removed += removed  # already noted per-pixel

    # Pass 6 — duplicate draw elimination ────────────────────────────────────

    def _pass_duplicate_draw(self):
        """
        Remove immediately consecutive DRAW_PIXEL instructions that are
        identical (same op + same args). This can happen from generated loops
        in user code.
        """
        new_ir: List[IRInstruction] = []
        removed = 0
        prev: Optional[IRInstruction] = None
        for ins in self._ir:
            if (ins.op == "DRAW_PIXEL" and prev is not None
                    and prev.op == "DRAW_PIXEL"
                    and prev.args == ins.args):
                removed += 1
                continue
            new_ir.append(ins)
            prev = ins

        if removed:
            self._note(f"Removed {removed} duplicate DRAW_PIXEL instruction(s).", removed)
        self._ir = new_ir


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
        print("=== Before Optimization ===")
        print(dump_ir(ir))

        result = Optimizer(ir).optimize()
        print("\n=== After Optimization ===")
        print(dump_ir(result.ir))
        print()
        print(result.summary())
    except (LexerError, ParseError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
