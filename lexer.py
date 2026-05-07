"""
PixelForge Compiler — Phase 1: Lexical Analyzer (Lexer)
CS4031 Compiler Construction · Spring 2026
Team: Minaal Fatima Jilani · Wania Fatima · Sameer Rajani

Converts raw PixelForge source text into a flat list of tokens.
Each token carries: type, value, line number, column number.
"""

from dataclasses import dataclass
from typing import List


# ──────────────────────────────────────────────────────────────────────────────
#  Token definition
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Token:
    type: str
    value: object        # str or int depending on type
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line}:C{self.col})"


# ──────────────────────────────────────────────────────────────────────────────
#  Keyword → token-type mapping
# ──────────────────────────────────────────────────────────────────────────────

KEYWORDS = {
    # Statements
    "canvas":   "CANVAS",
    "color":    "COLOR",
    "draw":     "DRAW",
    "animate":  "ANIMATE",
    "fill":     "FILL",
    # Draw sub-commands
    "pixel":    "PIXEL",
    "square":   "SQUARE",
    "line":     "LINE",
    "circle":   "CIRCLE",
    "rect":     "RECT",
    "triangle": "TRIANGLE",
    # Animate sub-commands
    "move":     "MOVE",
    # Direction literals
    "left":     "DIRECTION",
    "right":    "DIRECTION",
    "up":       "DIRECTION",
    "down":     "DIRECTION",
    # Color function
    "rgb":      "RGB",
    # Named colors → COLOR_NAME
    "red":      "COLOR_NAME",
    "green":    "COLOR_NAME",
    "blue":     "COLOR_NAME",
    "yellow":   "COLOR_NAME",
    "white":    "COLOR_NAME",
    "black":    "COLOR_NAME",
    "cyan":     "COLOR_NAME",
    "magenta":  "COLOR_NAME",
    "orange":   "COLOR_NAME",
    "purple":   "COLOR_NAME",
    "pink":     "COLOR_NAME",
    "gray":     "COLOR_NAME",
    "grey":     "COLOR_NAME",
    "brown":    "COLOR_NAME",
    "lime":     "COLOR_NAME",
}


# ──────────────────────────────────────────────────────────────────────────────
#  LexerError
# ──────────────────────────────────────────────────────────────────────────────

class LexerError(Exception):
    pass


# ──────────────────────────────────────────────────────────────────────────────
#  Lexer
# ──────────────────────────────────────────────────────────────────────────────

class Lexer:
    """
    Tokenises a PixelForge source string.

    Usage:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
    """

    def __init__(self, src: str):
        self.src = src
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    # ── public entry point ──────────────────────────────────────────────────

    def tokenize(self) -> List[Token]:
        """Scan the entire source and return the token list."""
        while self.pos < len(self.src):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.src):
                break
            ch = self.src[self.pos]
            if ch.isdigit():
                self._lex_number()
            elif ch.isalpha() or ch == '_':
                self._lex_word()
            elif ch == '(':
                self._push("LPAREN", "(")
                self._advance()
            elif ch == ')':
                self._push("RPAREN", ")")
                self._advance()
            elif ch == ',':
                self._push("COMMA", ",")
                self._advance()
            else:
                raise LexerError(
                    f"[Lexer] Unexpected character '{ch}' "
                    f"at line {self.line}, col {self.col}"
                )

        self._push("EOF", "<EOF>")
        return self.tokens

    # ── private helpers ─────────────────────────────────────────────────────

    def _advance(self):
        self.pos += 1
        self.col += 1

    def _push(self, token_type: str, value):
        self.tokens.append(Token(token_type, value, self.line, self.col))

    def _skip_whitespace_and_comments(self):
        while self.pos < len(self.src):
            ch = self.src[self.pos]
            if ch in (' ', '\t', '\r'):
                self._advance()
            elif ch == '\n':
                self.pos += 1
                self.line += 1
                self.col = 1
            elif ch == '#':                         # line comment
                while self.pos < len(self.src) and self.src[self.pos] != '\n':
                    self.pos += 1
            else:
                break

    def _lex_number(self):
        start_col = self.col
        start_line = self.line
        start = self.pos
        while self.pos < len(self.src) and self.src[self.pos].isdigit():
            self._advance()
        value = int(self.src[start:self.pos])
        self.tokens.append(Token("NUMBER", value, start_line, start_col))

    def _lex_word(self):
        start_col = self.col
        start_line = self.line
        start = self.pos
        while self.pos < len(self.src) and (self.src[self.pos].isalpha() or self.src[self.pos] == '_'):
            self._advance()
        word = self.src[start:self.pos].lower()
        token_type = KEYWORDS.get(word, "IDENTIFIER")
        self.tokens.append(Token(token_type, word, start_line, start_col))


# ──────────────────────────────────────────────────────────────────────────────
#  CLI helper — run as script to debug token output
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    src = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    lexer = Lexer(src)
    try:
        tokens = lexer.tokenize()
        print(f"{'#':<5} {'TYPE':<14} {'VALUE':<16} {'LINE':<6} {'COL'}")
        print("-" * 55)
        for i, tok in enumerate(tokens):
            print(f"{i:<5} {tok.type:<14} {str(tok.value):<16} {tok.line:<6} {tok.col}")
    except LexerError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
