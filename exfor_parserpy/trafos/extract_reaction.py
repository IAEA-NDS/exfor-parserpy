import sys
import re
import pyparsing
import json
from collections.abc import Iterable

sys.path.append("..")
from exfor_parserpy.utils.reaction_expr_parse import *



def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def parse_parenthesis(expr, ofs):
    pos_left = []
    pos_right = []
    count_left = 0
    count_right = 0

    while ofs < len(expr):

        if expr[ofs] == "(":
            count_left += 1
            pos_left += [ofs]

        if expr[ofs] == ")":
            count_right += 1
            pos_right += [ofs]

        ofs += 1
        if count_left == count_right:
            break

    assert len(pos_left) == len(pos_right)
    return pos_left, pos_right


def split_sfs(sf49):
    if sf49:
        sf4 = len(sf49) > 0 and sf49[0] or None
        sf5 = len(sf49) > 1 and sf49[1] or None
        sf6 = len(sf49) > 2 and sf49[2] or None
        sf7 = len(sf49) > 3 and sf49[3] or None
        sf8 = len(sf49) > 4 and sf49[4] or None
        sf9 = len(sf49) > 5 and sf49[5] or None
    return {"sf4": sf4,
            "sf5": sf5,
            "sf6": sf6,
            "sf7": sf7,
            "sf8": sf8,
            "sf9": sf9,}


def parse_reaction(reaction_str):
    # pos_left, pos_right = parse_parenthesis(reaction_str, 0)
    # print(pos_left, pos_right)

    charinreaction = "-+/,*. "
    thecontent = pyparsing.Word(
                    pyparsing.alphanums + charinreaction
                )
    parentheses = pyparsing.nestedExpr("(", ")", content=thecontent)
    free_text   = pyparsing.nestedExpr("(", ")", content=thecontent).suppress() + pyparsing.rest_of_line(reaction_str)
    a = parentheses.parseString(reaction_str).as_list()
    b = free_text.parseString(reaction_str)  

    reaction_node = {}

    nuclide = re.compile("([0-9]{1,3}-[A-Z0-9]{1,3}-[0-9]{1,3})$")
    process = re.compile("([A-Z0-9]{1,3},[A-Z0-9]{1,4})")
    params = re.compile("([A-Z0-9-+,\/\(\)]*)")

    node = 0
    reaction_node = {}
    subnode = {}

    for exp in list(flatten(a)):
        if exp.startswith(("/", "*", "-", "+")):
            node += 1
            reaction_node[node] = subnode
            subnode = {}

            if exp.startswith("/"):
                subnode["node_arithmetic_exp"] = "ratio"
            elif exp.startswith("*"):
                subnode["node_arithmetic_exp"] = "product"
            elif exp.startswith("+"):
                subnode["node_arithmetic_exp"] = "plus"
            elif exp.startswith("-"):
                subnode["node_arithmetic_exp"] = "minus"

        elif nuclide.match(exp):
            subnode["target"] = nuclide.match(exp).groups()[0]

        elif process.match(exp):
            subnode["process"] = process.match(exp).groups()[0]

        elif params.match(exp):
            subnode.update(split_sfs(params.match(exp).groups()[0].split(",")))
            reaction_node[node] = subnode
    
    if b:
        reaction_node["freetext"] = " ".join(b)

    print(json.dumps(reaction_node, indent=1))
        


