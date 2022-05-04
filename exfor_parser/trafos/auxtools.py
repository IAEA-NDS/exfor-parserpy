def exfor_iterator(exfor_dic):
    # recursively scan an EXFOR data structure
    # in a top down way
    def recfun(dic):
        if isinstance(dic, dict):
            yield dic
            for key, item in dic.items():
                yield from recfun(item)
    yield from recfun(exfor_dic)

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

def parse_product(expr, callback, ofs):
    print(f'parse product {expr[ofs:]}')
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '(':
        leftval, ofs = parse_addition(expr, callback, ofs+1)
        next_char, ofs = get_next_char(expr, ofs)
        if next_char != ')':
            raise ValueError('bracket not closed')
        ofs += 1
    elif next_char.isalpha() or next_char.isdigit():
        leftval, ofs = get_number(expr, callback, ofs) 
    # either a product and we continue expanding
    # or a number/symbol and we stop here
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '*':
        rightval, ofs = parse_product(expr, callback, ofs+1)
        return leftval * rightval, ofs
    else:
        return leftval, ofs

def parse_addition(expr, callback, ofs): 
    leftval, ofs = parse_product(expr, callback, ofs)
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '+':
        rightval, ofs = parse_addition(expr, callback, ofs+1) 
        return leftval + rightval, ofs
    elif next_char == '-':
        rightval, ofs = parse_addition(expr, callback, ofs+1)
        return leftval - rightval, ofs
    else:
        return leftval, ofs

    
def idfun(x):
    if x=='a':
        return 5
    else:
        return 10

parse_addition('7+5', idfun, ofs=0)

parse_addition('(3*(2+7*5)-1)*(5+1*(2-1))', idfun, ofs=0)

parse_addition('(3+2)-1', idfun, ofs=0)




