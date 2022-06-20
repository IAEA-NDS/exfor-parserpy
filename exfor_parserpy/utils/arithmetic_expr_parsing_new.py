############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/06/20
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################


def get_next_char(expr, ofs):
    while ofs < len(expr) and expr[ofs] == " ":
        ofs += 1
    if ofs == len(expr):
        return None, ofs
    else:
        return expr[ofs], ofs


def parse_symbol(expr, ofs, parse_usersym):
    next_char, ofs = get_next_char(expr, ofs)
    leftnode = {}
    if next_char == "-":
        leftnode["type"] = "neg"
        childnode, ofs = parse_symbol(expr, ofs + 1, parse_usersym)
        leftnode["children"] = [childnode]
    elif next_char == "(":
        leftnode["type"] = "bracket"
        childnode, ofs = parse_addition(expr, ofs + 1, parse_usersym)
        leftnode["children"] = [childnode]
        next_char, ofs = get_next_char(expr, ofs)
        if next_char != ")":
            raise ValueError("bracket not closed")
        ofs += 1
    else:
        leftnode, ofs = parse_usersym(expr, ofs)
    # division needs to be treated specially
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == "/":
        rightnode, ofs = parse_symbol(expr, ofs + 1, parse_usersym)
        divnode = {}
        divnode["type"] = "div"
        divnode["children"] = [leftnode, rightnode]
        return divnode, ofs
    else:
        return leftnode, ofs


def parse_product(expr, ofs, parse_usersym):
    leftnode, ofs = parse_symbol(expr, ofs, parse_usersym)
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == "*":
        rightnode, ofs = parse_product(expr, ofs + 1, parse_usersym)
        prodnode = {}
        prodnode["type"] = "prod"
        prodnode["children"] = [leftnode, rightnode]
        return prodnode, ofs
    else:
        return leftnode, ofs


def parse_addition(expr, ofs, parse_usersym):
    leftnode, ofs = parse_product(expr, ofs, parse_usersym)
    next_char, ofs = get_next_char(expr, ofs)
    if next_char == "+":
        rightnode, ofs = parse_addition(expr, ofs + 1, parse_usersym)
        addnode = {}
        addnode["type"] = "add"
        addnode["children"] = [leftnode, rightnode]
        return addnode, ofs
    elif next_char == "-":
        rightnode, ofs = parse_addition(expr, ofs + 1, parse_usersym)
        subnode = {}
        subnode["type"] = "sub"
        subnode["children"] = [leftnode, rightnode]
        return subnode, ofs
    else:
        return leftnode, ofs


def parse_arithm_expr(expr, parse_usersym, ofs=0):
    return parse_addition(expr, ofs, parse_usersym)
