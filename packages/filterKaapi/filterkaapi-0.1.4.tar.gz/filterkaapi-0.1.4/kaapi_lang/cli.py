import sys
from .main import run_code

def is_complete_kaapi_code(code: str) -> bool:
    lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
    if not lines:
        return False

    open_blocks = 0
    for line in lines:
        if line.startswith("varai") or line.startswith("seyyu"):
            open_blocks += 1
        elif line == "end" or line == "mudinchu":
            open_blocks -= 1

    return open_blocks <= 0

def repl():
    print("Start writing your Hot filter Kaapi (type 'exit' to quit REPL')")
    buffer = ""

    while True:
        try:
            prompt = ">>> " if not buffer else "... "
            line = input(prompt)

            if line.strip().lower() == "exit":
                break

            buffer += line + "\n"

            if is_complete_kaapi_code(buffer):
                try:
                    run_code(buffer)
                except Exception as e:
                    print(f"Error: {e}")
                buffer = ""
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Kaapi REPL.")
            break


def main():
    """Entry point for `kaapi` command."""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, "r") as f:
            code = f.read()
        run_code(code)
    else:
        repl()


if __name__ == "__main__":
    main()
