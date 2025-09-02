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
            elif vtype == "LIST":
                parsedList = []
                for e in value:
                    if e.isdigit():
                        parsedList.append(int(e))
                    elif e.startswith("\"") and e.endswith("\""):
                        parsedList.append(e[1:-1])
                    elif e in symbol_table:
                        parsedList.append(symbol_table[e])
                    else:
                        parsedList.append(e)
                symbol_table[var_name] = parsedList
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
                if "[" in value and value.endswith("]"):
                    var_name,index = value[:-1].split("[",1)
                    index = evaluate(index.strip())
                    if var_name in symbol_table and isinstance(symbol_table[var_name],list):
                        print(symbol_table[var_name][index])
                    else:
                        print("INVALID LIST ACCESS",value)
                elif value in symbol_table:
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
        
        elif token[0] == "PUSH":
            _, var_name,raw_value = token
            if var_name in symbol_table and isinstance(symbol_table[var_name],list):
                value = evaluate(raw_value)
                symbol_table[var_name].append(value)
        
        elif token[0] == "POP":
            _,var_name= token
            if var_name in symbol_table and isinstance(symbol_table[var_name],list):
                symbol_table[var_name].pop()
        
        elif token[0] == "REMOVE":
            _, var_name, raw_value = token
            if var_name in symbol_table and isinstance(symbol_table[var_name],list):
                value = evaluate(raw_value)
                symbol_table[var_name].remove(value)
        
        elif token[0] == "LEN":
            _, var_name = token
            if var_name in symbol_table and isinstance(symbol_table[var_name],list):
                print(len(symbol_table[var_name]))

        elif token[0] == "ERROR":
            _,error_msg,value = token
            print(error_msg,value)