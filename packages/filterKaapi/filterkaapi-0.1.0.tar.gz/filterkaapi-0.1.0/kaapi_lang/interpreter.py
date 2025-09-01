import sys
from .lexer import lexer

symbol_table = {}
function_table = {}


def evaluate(expr):
    tokens = expr.split()
    for i,token in enumerate(tokens):
        if token in symbol_table:
            val = symbol_table[token]
            if isinstance(val,str) and not(val.startswith("\"") and val.endswith("\"")):
                tokens[i] = f"\"{val}\""
            else:
                tokens[i] = str(val)
    expr_value = " ".join(tokens)
    return eval(expr_value)

def evaluate_lines(line):
    line = line.strip()
    if line.startswith("kaapi"):
        arg = line[len("kaapi"):].strip()
        if arg.startswith("\"") and arg.endswith("\""):
            print(arg[1:-1])
        elif arg.isdigit():
            print(arg)
        elif any(op in arg for op in ["+","-","*","/","%","//",">","<","==",">=","<=", "!="]):
            print(evaluate(arg))
        else:
            if arg in symbol_table:
                print(symbol_table[arg])
    
    elif line.startswith("vechiko"):
        var_parts = line[len("vechiko"):].strip().split("=",1)
        var_name = var_parts[0].strip()
        var_value = var_parts[1].strip()
        if var_value.startswith("\"") and var_value.endswith("\""):
            symbol_table[var_name] = var_value
        elif var_value.isdigit():
            symbol_table[var_name] = int(var_value)
        elif any(op in var_value for op in ["+","-","*","/","%","//",">","<","==",">=","<=", "!="]):
            symbol_table[var_name] = evaluate(var_value)
        elif var_value in symbol_table:
            symbol_table[var_name] = symbol_table[var_value]
    
    elif "iruntha" in line and "ilana" in line:
        condition,rest = line.split("iruntha",1)
        true_stmt,false_stmt = rest.split("ilana",1)
        if evaluate(condition.strip()):
            evaluate_lines(true_stmt.strip())
        else:
            evaluate_lines(false_stmt.strip())

def openFile(filename):
    with open(filename, "r") as f:
        return f.read()

def fetch_code():
    from .parser import parser
    data = openFile(sys.argv[1])
    tokens = lexer(data)
    parser(tokens)
    print(tokens)

if __name__ == "__main__":
    fetch_code()
