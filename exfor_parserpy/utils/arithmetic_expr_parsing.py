############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/05/04
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################

# functions to parse arithmetic expressions
# vardic is a dictionary used to substitute names in an
# arithmetic expression by numbers or another name.
# the function to be invoked by the user here is
# eval_arithm_expr

def get_number(expr, vardic, ofs, comp, ops):
    curstr = ''
    while (ofs < len(expr) and
           expr[ofs] not in ' ' + ops): 
        curstr += expr[ofs]
        ofs +=1
    # try to obtain a number
    if comp:
        try:
            number = float(curstr)
            return number, ofs
        except:
            pass
        # obtain a value from the dictionary
        # if the value is not found we assume 1
        # which is the desired behavior in compound
        # units
        number = vardic.get(curstr, 1)
        return number, ofs
    else:
        # we only substitute names in the arithmetic
        # expression string but do not try to calculate something
        if curstr in vardic:
            curstr = vardic[curstr]
        return curstr, ofs

def get_next_char(expr, ofs):
    while (ofs < len(expr) and not expr[ofs].isdigit() and
           not expr[ofs].isalpha() and expr[ofs] not in ('+','-','*','/','(',')')):
        ofs += 1
    if ofs == len(expr):
        return None, ofs
    else:
        return expr[ofs], ofs

def eval_symbol(expr, vardic, ofs, comp, ops):
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '-':
        leftval, ofs = eval_symbol(expr, vardic, ofs+1, comp, ops)
        if comp:
            leftval = -leftval
        else:
            leftval = '-' + leftval
    elif next_char == '(':
        leftval, ofs = eval_addition(expr, vardic, ofs+1, comp, ops)
        next_char, ofs = get_next_char(expr, ofs)
        if next_char != ')':
            raise ValueError('bracket not closed')
        if not comp:
            leftval = '(' + leftval + ')'
        ofs += 1
    elif next_char.isalpha() or next_char.isdigit() or '-':
        leftval, ofs = get_number(expr, vardic, ofs, comp, ops) 
    # division needs to be treated specially
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '/':
        rightval, ofs = eval_symbol(expr, vardic, ofs+1, comp, ops)
        if comp:
            return leftval / rightval, ofs 
        else:
            return leftval + '/' + rightval, ofs
    else:
        return leftval, ofs

def eval_product(expr, vardic, ofs, comp, ops):
    leftval, ofs = eval_symbol(expr, vardic, ofs, comp, ops)
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '*':
        rightval, ofs = eval_product(expr, vardic, ofs+1, comp, ops)
        if comp:
            return leftval * rightval, ofs
        else:
            return leftval + '*' + rightval, ofs
    else:
        return leftval, ofs

def eval_addition(expr, vardic, ofs, comp, ops): 
    leftval, ofs = eval_product(expr, vardic, ofs, comp, ops)
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == '+':
        rightval, ofs = eval_addition(expr, vardic, ofs+1, comp, ops) 
        if comp:
            return leftval + rightval, ofs
        else:
            return leftval + '+' + rightval, ofs
    elif next_char == '-':
        rightval, ofs = eval_addition(expr, vardic, ofs+1, comp, ops)
        if comp:
            return leftval - rightval, ofs
        else:
            return leftval + '-' + rightval, ofs
    else:
        return leftval, ofs

def eval_arithm_expr(expr, vardic=None, comp=True, ops='+-*/'):
    if vardic is None:
        vardic = {}
    value, _ = eval_addition(expr, vardic, ofs=0, comp=comp, ops=ops)
    return value
    
