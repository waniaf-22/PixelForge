"""
PixelForge Compiler -- Backend API Server
CS4031 Compiler Construction . Spring 2026
Team: Minaal Fatima Jilani . Wania Fatima . Sameer Rajani

Flask backend that exposes the compiler pipeline as a REST API.
The frontend sends source code and receives tokens, AST, semantic
analysis results, IR, and optimizer output as JSON.
"""

import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Force UTF-8 output so box-drawing chars work on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from lexer import Lexer, LexerError
from parser import Parser, ParseError, pretty_print_ast
from semantic_analyzer import SemanticAnalyzer
from ir_generator import IRGen
from optimizer import Optimizer

app = Flask(__name__)
CORS(app)  # allow the HTML file to call this from any origin


# ------------------------------------------------------------------------------
#  Terminal colour helpers
# ------------------------------------------------------------------------------

CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
ORANGE  = "\033[33m"
DIM     = "\033[90m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

def banner(title, color=CYAN):
    line = "-" * 62
    print(f"\n{color}{BOLD}{line}{RESET}")
    print(f"{color}{BOLD}  {title}{RESET}")
    print(f"{color}{BOLD}{line}{RESET}")

def section(title, color=YELLOW):
    print(f"\n{color}{BOLD}>>  {title}{RESET}")
    print(f"{DIM}{'-' * 42}{RESET}")


# ------------------------------------------------------------------------------
#  /api/compile  -- full pipeline
# ------------------------------------------------------------------------------

@app.route("/api/compile", methods=["POST"])
def compile_source():
    data = request.get_json(force=True)
    src  = data.get("source", "")

    banner("[*] PIXELFORGE COMPILER PIPELINE", CYAN)
    print(f"{DIM}Source ({len(src)} chars):{RESET}")
    for i, ln in enumerate(src.splitlines(), 1):
        print(f"  {DIM}{i:>3}|{RESET}  {ln}")

    result = {
        "ok": False,
        "phase": None,
        "error": None,
        "tokens": [],
        "ast": None,
        "semantic": {"errors": [], "warnings": []},
        "ir": [],
        "ir_optimized": [],
        "optimizer_notes": [],
        "optimizer_removed": 0,
    }

    # -- Phase 1: Lexer --------------------------------------------------------
    section("PHASE 1 -- LEXER")
    try:
        tokens = Lexer(src).tokenize()
    except LexerError as e:
        print(f"{RED}  [X]  Lexer Error: {e}{RESET}")
        result["phase"] = "lexer"
        result["error"] = str(e)
        return jsonify(result)

    non_eof = [t for t in tokens if t.type != "EOF"]
    print(f"{GREEN}  [OK]  {len(non_eof)} token(s) produced{RESET}\n")
    for t in non_eof:
        print(f"    {CYAN}{t.type:<20}{RESET}{YELLOW}{str(t.value):<20}{RESET}{DIM}L{t.line}:C{t.col}{RESET}")

    result["tokens"] = [
        {"type": t.type, "value": str(t.value), "line": t.line, "col": t.col}
        for t in tokens
    ]

    # -- Phase 2: Parser -------------------------------------------------------
    section("PHASE 2 -- PARSER")
    try:
        ast = Parser(tokens).parse()
    except ParseError as e:
        print(f"{RED}  [X]  Parse Error: {e}{RESET}")
        result["phase"] = "parser"
        result["error"] = str(e)
        return jsonify(result)

    ast_text = pretty_print_ast(ast)
    print(f"{GREEN}  [OK]  AST built -- {len(ast.body)} top-level statement(s){RESET}\n")
    for ln in ast_text.splitlines():
        print(f"    {ln}")

    result["ast"] = ast_text

    # -- Phase 3: Semantic Analyzer --------------------------------------------
    section("PHASE 3 -- SEMANTIC ANALYZER")
    sem = SemanticAnalyzer(ast).analyze()
    result["semantic"]["errors"]   = [{"message": e.message, "line": e.line} for e in sem.errors]
    result["semantic"]["warnings"] = [{"message": w.message, "line": w.line} for w in sem.warnings]

    for w in sem.warnings:
        print(f"  {YELLOW}[!]  L{w.line}: {w.message}{RESET}")
    for e in sem.errors:
        print(f"  {RED}[X]  L{e.line}: {e.message}{RESET}")

    if not sem.ok:
        print(f"\n{RED}  [X]  Semantic analysis FAILED -- {len(sem.errors)} error(s){RESET}")
        result["phase"] = "semantic"
        result["error"] = f"{len(sem.errors)} semantic error(s) found."
        return jsonify(result)

    print(f"{GREEN}  [OK]  Semantic analysis PASSED -- no errors{RESET}")

    # -- Phase 4: IR Generator -------------------------------------------------
    section("PHASE 4 -- IR GENERATOR")
    ir = IRGen().generate(ast)
    print(f"{GREEN}  [OK]  {len(ir)} IR instruction(s) generated{RESET}\n")
    for i, ins in enumerate(ir):
        print(f"    {DIM}{i:>3}{RESET}  {MAGENTA}{ins.op:<24}{RESET}{ORANGE}{ins.args}{RESET}")

    result["ir"] = [
        {"idx": i, "op": ins.op, "args": ins.args}
        for i, ins in enumerate(ir)
    ]

    # -- Phase 5: Optimizer ----------------------------------------------------
    section("PHASE 5 -- OPTIMIZER")
    opt = Optimizer(ir).optimize()

    if opt.notes:
        for note in opt.notes:
            print(f"  {ORANGE}->  {note}{RESET}")
    else:
        print(f"  {DIM}No optimizations applied.{RESET}")

    print(f"\n{GREEN}  [OK]  {len(opt.ir)} instruction(s) remaining  (removed: {opt.removed}){RESET}\n")
    for i, ins in enumerate(opt.ir):
        print(f"    {DIM}{i:>3}{RESET}  {MAGENTA}{ins.op:<24}{RESET}{ORANGE}{ins.args}{RESET}")

    result["ir_optimized"]     = [{"idx": i, "op": ins.op, "args": ins.args} for i, ins in enumerate(opt.ir)]
    result["optimizer_notes"]   = opt.notes
    result["optimizer_removed"] = opt.removed

    result["ok"]    = True
    result["phase"] = "done"

    banner(
        f"[DONE]  tokens:{len(non_eof)}  raw-ir:{len(ir)}  "
        f"optimized-ir:{len(opt.ir)}  removed:{opt.removed}",
        GREEN
    )
    return jsonify(result)


# ------------------------------------------------------------------------------
#  /api/health  -- simple health check
# ------------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    print(f"{DIM}[health] ping received{RESET}")
    return jsonify({"status": "ok", "compiler": "PixelForge v1.0"})


# ------------------------------------------------------------------------------
#  /api/source  -- serve compiler source code
# ------------------------------------------------------------------------------

@app.route("/api/source", methods=["GET"])
def get_source():
    files = ["app.py", "lexer.py", "parser.py", "semantic_analyzer.py", "ir_generator.py", "optimizer.py"]
    code = {}
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                code[f] = fh.read()
        except Exception as e:
            code[f] = f"# Error reading file: {e}"
    print(f"{DIM}[source] served {len(files)} compiler files{RESET}")
    return jsonify(code)


# ------------------------------------------------------------------------------
#  /  -- serve main frontend IDE
# ------------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    from flask import send_file
    return send_file("PixelForge_Compiler.html")



if __name__ == "__main__":
    print(f"\n{CYAN}{BOLD}{'=' * 62}{RESET}")
    print(f"{CYAN}{BOLD}  PixelForge Compiler Backend  .  CS4031  .  Spring 2026{RESET}")
    print(f"{CYAN}{BOLD}  Minaal Fatima Jilani  .  Wania Fatima  .  Sameer Rajani{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 62}{RESET}")
    print(f"{GREEN}  Listening on http://127.0.0.1:5000{RESET}\n")
    app.run(debug=True, port=5000)
