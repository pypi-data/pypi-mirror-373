import sys
import os
from .main import run_code  # ✅ Matches the renamed function

def main():
    if len(sys.argv) < 2:
        print("Usage: kaapi <filename.kaapi>")
        sys.exit(1)

    filename = sys.argv[1]
    filepath = os.path.abspath(filename)

    if not os.path.exists(filepath):
        print(f"Error: File '{filename}' not found in {os.getcwd()}")
        sys.exit(1)

    try:
        with open(filepath, "r") as f:
            code = f.read()
        run_code(code)  # ✅ Calls the right function
    except Exception as e:
        print(f"Runtime Error: {e}")
        sys.exit(1)
