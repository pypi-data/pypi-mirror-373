# ☕ FilterKaapi Language

FilterKaapi is a **Tamil-inspired programming language** written in Python.  
Just like Chennai's famous filter coffee, this language is simple, strong, and gives a warm kick to coding!

🖋️ **Keywords are in Tamil** to make coding feel closer to home:

- `kaapi` → print (like pouring kaapi ☕)
- `vechiko` → variable declaration (means "keep it")
- `iruntha ... ilana ...` → if ... else
- `varai` → while loop

---

## 🚀 Features

- 📝 **Tamil keywords** for programming basics
- ➕ Arithmetic operations (`+`, `-`, `*`, `/`, `%`, `//`)
- 🔑 Variables with `vechiko`
- 🔍 Conditional logic with `iruntha ... ilana ...`
- 🔁 `varai` for loops
- 🖥️ REPL and script execution support

---

## 📦 Installation

For now, install from source:

```bash
git clone https://github.com/yourusername/filterKaapi.git
cd filterKaapi
pip install .
```

### After installation, run:

```bash
kaapi main.kaapi
```

Or start the interactive REPL:

```bash
kaapi
```

### 🔤 Language Syntax

Printing

```bash
kaapi "Vanakkam Chennai!"
```

Variables

```bash
vechiko x = 10
kaapi x
```

Arithmetic

```bash
kaapi 5 + 3 * 2
```

If/Else

```bash
5 > 3 iruntha kaapi "Periya number" ilana kaapi "Siriya number"
```

While Loop

```bash
vechiko i = 0
varai i < 5
    kaapi i
    vechiko i = i + 1
end
```

## 🛠 Project Structure

```bash
kaapi_lang/
 ├── __init__.py
 ├── cli.py           # CLI entry point
 ├── interpreter.py   # Evaluator
 ├── lexer.py         # Tokenizer
 ├── parser.py        # Parser
 └── main.py          # Runner

setup.py              # For packaging
```

# 👨‍💻 Author

Created with ❤️ in Chennai by Chiddesh Ram\
Inspired by strong Filter Kaapi and a love for coding.
