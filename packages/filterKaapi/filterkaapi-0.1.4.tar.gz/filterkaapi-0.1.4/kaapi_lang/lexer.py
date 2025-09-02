from .functions import push,pop,remove,length

def lexer(data):
    tokens = []
    lines = data.split("\n")

    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1 
            continue
        
        elif line.startswith("vechiko"):
            var_parts = line[len("vechiko"):].strip().split("=",1)
            var_name = var_parts[0].strip()
            var_value = var_parts[1].strip()

            if var_value.startswith("\"") and var_value.endswith("\""):
                tokens.append(("VAR",var_name,"STRING",var_value[1:-1]))
            elif var_value.isdigit():
                tokens.append(("VAR",var_name,"NUM",var_value))
            elif any(op in var_value for op in ["+","-","*","/","%","//",">","<","==",">=","<=", "!=","(",")"]):
                tokens.append(("VAR",var_name,"EXPR",var_value))
            elif var_value.startswith("[") and var_value.endswith("]"):
                elements = [e.strip() for e in var_value[1:-1].split(",") if e.strip()]
                tokens.append(("VAR",var_name,"LIST",elements))
            else:
                tokens.append(("VAR",var_name,"VAR",var_value))

        elif line.startswith("kaapi"):
            arg = line[len("kaapi"):].strip()
            if arg.startswith("\"") and arg.endswith("\""):
                tokens.append(("PRINT","STRING",arg[1:-1]))
            elif arg.isdigit():
                tokens.append(("PRINT","NUM",arg))
            elif any(op in arg for op in ["+","-","*","/","%","//",">","<","==",">=","<=", "!=","(",")"]):
                tokens.append(("PRINT","EXPR",arg))
            else:
                tokens.append(("PRINT","VAR",arg))
        
        elif "iruntha" in line and "ilana" in line:
            condition,rest = line.split('iruntha')
            true_stmt,false_stmt = rest.split("ilana")
            tokens.append(("IF",condition,true_stmt,false_stmt))
        
        elif line.startswith("seyyu"):
            header = line[len("seyyu"):].strip()
            if "(" in header and ")" in header:
                func_name,params = header.split("(",1)
                params = params[:-1].strip()
                params = [p.strip() for p in params.split(",")] if params else []

                body = []
                i += 1
                while i < len(lines) and not lines[i].strip().endswith("mudinchu"):
                    body.append(lines[i].strip())
                    i+= 1
            tokens.append(("FUNC_DEF",func_name,params,body))
        
        elif "(" in line and ")" in line:
            func_name,args = line.split("(",1)
            args = args[:-1].strip()
            args = [a.strip() for a in args.split(",")] if args else []
            tokens.append(("FUNC_CALL",func_name,args))
        
        
        elif line.startswith("machan"):
            i+= 1
            continue
        
        elif line.startswith("varai"):
            condition = line[len("varai"):].strip()
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().endswith("end"):
                body.append(lines[i].strip())
                i+= 1
            tokens.append(("LOOP",condition,body))
        
        elif line.startswith("notepaniko"):
            rest = line[len("notepaniko"):].strip()
            if " " in rest:
                var_name,msg = rest.split(" ",1)
                msg = msg.strip()
                if msg.startswith("\"") and msg.endswith("\""):
                    msg = msg[1:-1]
                else:
                    var_name = rest
                    msg = msg[1:-1]
            tokens.append(("INPUT",var_name,msg))
        
        elif line.startswith("push"):
            var_name,value = push(line)
            tokens.append(("PUSH", var_name, value))
        
        elif line.startswith("pop"):
            var_name = pop(line)
            tokens.append(("POP",var_name))
        
        elif line.startswith("remove"):
            var_name,value = remove(line)
            tokens.append(("REMOVE",var_name,value))

        elif line.startswith("len"):
            var_name = length(line)
            tokens.append(("LEN",var_name))

        else:
            tokens.append(("ERROR","SYNTAX ERROR",line))
        i+= 1

    return tokens