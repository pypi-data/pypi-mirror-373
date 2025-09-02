import sys
from .lexer import lexer
from .functions import push,pop,remove
import re

symbol_table = {}
function_table = {}


def evaluate(expr):
    def repl_var(match):
        var = match.group(0)
        if var in symbol_table:
            val = symbol_table[var]
            # Wrap strings in quotes
            if isinstance(val, str):
                return f'"{val}"'
            else:
                return str(val)
        return var
    expr_fixed = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', repl_var, expr)
    
    try:
        return eval(expr_fixed)
    except Exception as e:
        print("Evaluation error:", e)
        return None

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
        elif "[" in arg and arg.endswith("]"):
            var_name,index = arg[:-1].split("[",1)
            index = evaluate(index.strip())
            if var_name in symbol_table and isinstance(symbol_table[var_name],list):
                print(symbol_table[var_name][index])
            else:
             print("INVALID LIST ACCESS", arg)
        else:
            if arg in symbol_table:
                print(symbol_table[arg])
            else:
                print("UNDEFINED VARIABLE",arg)
    
    elif line.startswith("vechiko"):
        var_parts = line[len("vechiko"):].strip().split("=",1)
        var_name = var_parts[0].strip()
        var_value = var_parts[1].strip()
        if var_value.startswith("\"") and var_value.endswith("\""):
            symbol_table[var_name] = var_value
        elif var_value.isdigit():
            symbol_table[var_name] = int(var_value)
        elif any(op in var_value for op in ["+","-","*","/","%","//",">","<","==",">=","<=", "!=","(",")"]):
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
    
    elif line.startswith("notepaniko"):
        rest = line[len("notepaniko"):].strip()
        if " " in rest:
            var_name,msg = rest.split(" ",1)
            msg = msg.strip()
            if msg.startswith("\"") and msg.endswith("\""):
                msg = msg[1:-1]
            else:
                var_name = rest
                msg = ""
        user_input = input(msg+": ")
        if user_input.isdigit():
            symbol_table[var_name] = int(user_input)
        else:
            symbol_table[var_name] = user_input

    
    elif line.startswith("push"):
        var_name,raw_value = push(line)
        if var_name in symbol_table and isinstance(symbol_table[var_name],list):
            value = evaluate(raw_value)
            symbol_table[var_name].append(value)
    
    elif line.startswith("pop"):
        var_name = pop(line)
        if var_name in symbol_table and isinstance(symbol_table[var_name],list):
            symbol_table[var_name].pop()
    
    elif line.startswith("remove"):
        var_name,raw_value = remove(line)
        if var_name in symbol_table and isinstance(symbol_table[var_name],list):
            value = evaluate(raw_value)
            symbol_table[var_name].remove(value)


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
