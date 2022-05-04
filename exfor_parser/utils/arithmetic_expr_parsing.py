# functions to parse arithmetic expressions
# callback is a function that is invoked if
# the conversion from a sequence of symbols (digits or characters)
# to a number via float fails. So callback can be used to
# substitute variables by their values

def get_number(expr, callback, ofs):
    curstr = ''
    while (ofs < len(expr) and
           expr[ofs] not in (' ','+','-','*','/',')')): 
        curstr += expr[ofs]
        truthval = expr[ofs] not in (' ','+','-','*','/',')')
        ofs +=1
    # try to obtain a number
    try:
        number = float(curstr)
        return number, ofs
    except:
        pass
    # try to obtain a value using the callback
    number = callback(curstr)
    return number, ofs

def get_next_char(expr, ofs):
    while (ofs < len(expr) and not expr[ofs].isdigit() and
           not expr[ofs].isalpha() and expr[ofs] not in ('+','-','*','/','(',')')):
        ofs += 1
    if ofs == len(expr):
        return None, ofs
    else:
        return expr[ofs], ofs

def eval_symbol(expr, callback, ofs):
    next_char, ofs = get_next_char(expr, ofs)
    print(f'next char is {next_char}')
    if next_char == '-':
        leftval, ofs = eval_symbol(expr, callback, ofs+1)
        leftval = -leftval
    elif next_char == '(':
        leftval, ofs = eval_addition(expr, callback, ofs+1)
        next_char, ofs = get_next_char(expr, ofs)
        if next_char != ')':
            raise ValueError('bracket not closed')
        ofs += 1
    elif next_char.isalpha() or next_char.isdigit() or '-':
        leftval, ofs = get_number(expr, callback, ofs) 
    # division needs to be treated specially
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '/':
        rightval, ofs = eval_symbol(expr, callback, ofs+1)
        return leftval / rightval, ofs 
    else:
        return leftval, ofs

def eval_product(expr, callback, ofs):
    leftval, ofs = eval_symbol(expr, callback, ofs)
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '*':
        rightval, ofs = eval_product(expr, callback, ofs+1)
        return leftval * rightval, ofs
    else:
        return leftval, ofs

def eval_addition(expr, callback, ofs): 
    leftval, ofs = eval_product(expr, callback, ofs)
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '+':
        rightval, ofs = eval_addition(expr, callback, ofs+1) 
        return leftval + rightval, ofs
    elif next_char == '-':
        rightval, ofs = eval_addition(expr, callback, ofs+1)
        return leftval - rightval, ofs
    else:
        return leftval, ofs

def idfun(x):
    return x

def eval_arithm_expr(expr, callback=None):
    def idfun(x):
        return x
    if callback is None:
        callback = idfun
    value, _ = eval_addition(expr, callback, ofs=0)
    return value
    
