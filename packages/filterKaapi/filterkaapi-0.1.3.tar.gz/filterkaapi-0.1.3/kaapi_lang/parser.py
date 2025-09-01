from .interpreter import evaluate, evaluate_lines, symbol_table, function_table

def parser(tokens):
    for token in tokens:
        
        if token[0] == "VAR":
            _, var_name,vtype,value = token
            if vtype == "STRING":
                symbol_table[var_name] = value
            elif vtype == "NUM":
                symbol_table[var_name] = int(value)
            elif vtype == "EXPR":
                symbol_table[var_name] = evaluate(value)
            else:
                symbol_table[var_name] = value
        
        elif token[0] == "PRINT":
            _,dtype,value = token
            if dtype == "STRING":
                print(value)
            elif dtype == "NUM":
                print(value)
            elif dtype == "EXPR":
                print(evaluate(value))
            elif dtype == "VAR":
                if value in symbol_table:
                    print(symbol_table[value])
                else:
                    print("UNDEFINED VARIABLE",value)
        
        elif token[0] == "IF":
            _, condition, true_stmt,false_stmt = token
            if evaluate(condition):
                evaluate_lines(true_stmt)
            else:
                evaluate_lines(false_stmt)
        
        elif token[0] == "FUNC_DEF":
            _,func_name,params,body = token
            function_table[func_name] = {"params":params,"body":body}
        
        elif token[0] == "FUNC_CALL":
            _,func_name,args = token
            if func_name in function_table:
                params = function_table[func_name]["params"]
                body = function_table[func_name]["body"]

                local_scope = {}
                for p,a in zip(params,args):
                    if a.startswith("\"") and a.endswith("\""):
                        local_scope[p] = f"\"{a[1:-1]}\""
                    elif a.isdigit():
                        local_scope[p] = int(a)
                    elif a in symbol_table:
                        local_scope[p] = symbol_table[a]
                    else:
                        local_scope[p] = evaluate(a)
                backup = dict(symbol_table)
                symbol_table.update(local_scope)
                for line in body:
                    evaluate_lines(line)
                symbol_table.clear()
                symbol_table.update(backup)
            else:
                print("UNDEFINED FUNCTION",func_name)
        
        elif token[0] == "LOOP":
            _,condition,body = token
            while evaluate(condition):
                for line in body:
                    evaluate_lines(line)
        

        elif token[0] == "INPUT":
            _, var_name,msg = token
            user_input = input(msg+": ")
            if user_input.isdigit():
                symbol_table[var_name] = int(user_input)
            else:
                symbol_table[var_name] = user_input

        elif token[0] == "ERROR":
            _,error_msg,value = token
            print(error_msg,value)