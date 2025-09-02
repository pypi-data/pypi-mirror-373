import sys
from kaapi_lang.lexer import lexer
from kaapi_lang.parser import parser

symbol_table = {}
function_table = {}

def run_code(code):
    tokens = lexer(code)
    parser(tokens)

def openFile(filename):
    with open(filename, "r") as f:
        return f.read()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = openFile(sys.argv[1])
        run_code(code)
    else:
        print("Usage: python main.py <filename>")
