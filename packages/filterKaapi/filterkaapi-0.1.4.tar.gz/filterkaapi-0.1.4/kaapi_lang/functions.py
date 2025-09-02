def push(code):
    code = code[len("push"):].strip()
    var_name,value = code.split("[",1)
    var_name = var_name.strip()
    value = value[:-1].strip()
    return var_name, value

def pop(code):
    var_name = code[len("pop"):].strip()
    return var_name

def remove(code):
    code = code[len("remove"):].strip()
    var_name,value = code.split("[",1)
    var_name = var_name.strip()
    value = value[:-1].strip()
    return var_name, value

def length(code):
    var_name = code[len("len"):].strip()
    return var_name