import os
import sys
import subprocess
from glc.lexer import Lexer, TokenType
from glc.parser import Parser
from glc.t2c import ASTtoC


def main():
    if len(sys.argv) != 2:
        print("Usage: goat <source-file.g>")
        sys.exit(1)

    source_file = sys.argv[1]

    # -------------------- Read source code --------------------
    if not os.path.isfile(source_file):
        print(f"File not found: {source_file}")
        sys.exit(1)

    with open(source_file, "r") as f:
        code = f.read()

    # -------------------- Lexing --------------------
    lexer = Lexer(code)
    tokens = []
    tok = lexer.next_token()
    while tok.type != TokenType.END:
        tokens.append(tok)
        tok = lexer.next_token()

    # -------------------- Parsing --------------------
    parser = Parser(tokens)
    func = parser.parse_function()

    # -------------------- AST to C --------------------
    compiler = ASTtoC()
    compiler.function(func)

    # -------------------- Write C code --------------------
    c_dir = "c"
    os.makedirs(c_dir, exist_ok=True)
    c_file = os.path.join(
        c_dir, os.path.splitext(os.path.basename(source_file))[0] + ".c"
    )
    with open(c_file, "w") as f:
        f.write(compiler.code)
    # print(f"C code written to {c_file}")

    # -------------------- Compile --------------------
    exe_name = os.path.splitext(os.path.basename(source_file))[0]
    exe_file = f"{exe_name}.exe" if os.name == "nt" else exe_name

    compiler_cmd = ["gcc", c_file, "-o", exe_file]

    try:
        subprocess.run(compiler_cmd, check=True)
        # print(f"Executable created: {exe_file}")
    except subprocess.CalledProcessError:
        print("Compilation failed. Make sure you have GCC installed and on your PATH.")
        sys.exit(1)

    # -------------------- Run executable --------------------
    try:
        # print("Running program:\n")
        subprocess.run([exe_file] if os.name == "nt" else ["./" + exe_file])
    except Exception as e:
        print(f"Failed to run executable: {e}")
