# 🐐 GLC (GoatLang Compiler)

**GLC** is a toy programming language that transpiles to **C** and then compiles into native executables.
It’s designed for learning about compilers, transpilers, and language design while keeping things simple.

---

## ✨ Features

* Variables: `int`, `float`, `bool`, `string`
* Arithmetic: `+`, `-`, `*`, `/`
* Comparisons: `<`, `>`, `==`, `!=`
* Print statements: `print(expr)`
* Conditionals: `if` / `else`
* Loops: `while`
* Basic string concatenation (`msg + "something"`)

---

## 📦 Installation

Clone the repo and install it locally in **editable** mode:

```bash
pip install goatlang==0.0.1
```

This installs the `glc` command into your environment.

---

## ▶️ Usage

### Compile & Run a program

Create a file `hello.g`:

```goat
fn main() {
    string msg = "Hello, GoatLang!"
    print(msg)
}
```

Compile and run:

```bash
glc hello.g
```

Output:

```
Hello, GoatLang!
```

### Another Example (loop, conditionals, math)

```goat
fn main() {
    int x = 42
    float y = 3.14
    bool flag = true

    print(x)
    print(y)
    print(flag)

    int sum = x + 10
    float product = y * 2.0
    print(sum)
    print(product)

    if sum > 50 {
        print("Sum is large!")
    } else {
        print("Sum is small!")
    }

    int counter = 0
    while counter < 5 {
        print(counter)
        counter = counter + 1
    }
}
```

---

## 📂 Project Structure

```
glc/
├── glc/             # Source code
│   ├── lexer.py     # Tokenizer
│   ├── parser.py    # Parser → AST
│   ├── t2c.py       # AST → C transpiler
│   └── main.py      # CLI entry point
├── examples/        # Example GoatLang programs
├── pyproject.toml   # Build config
└── README.md
```

---

## ⚡ How It Works

1. **Lexing** – source code → tokens
2. **Parsing** – tokens → AST (abstract syntax tree)
3. **Transpiling** – AST → C code
4. **Compiling** – C → native executable (via GCC/clang)
5. **Running** – GLC runs the binary automatically

---

## 🛠 Requirements

* Python ≥ 3.8
* GCC or Clang (for compiling generated C code)

---

## 🚧 Limitations

* No user-defined functions yet (only `fn main`)
* String concatenation is still basic (uses buffers + `strcpy/strcat`)
* Error messages are primitive
* No standard library (beyond `print`)

---
Do you have some issues with the language put them here: https://github.com/Narendrakumar-Suresh/goat-lang/issues

## 📜 License

MIT License © 2025 Naren
