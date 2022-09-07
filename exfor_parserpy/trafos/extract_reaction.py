import sys
import re
import pyparsing
import json
from collections.abc import Iterable


def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def split_sfs(sf49):
    if sf49:
        sf4 = len(sf49) > 0 and sf49[0] or None
        sf5 = len(sf49) > 1 and sf49[1] or None
        sf6 = len(sf49) > 2 and sf49[2] or None
        sf7 = len(sf49) > 3 and sf49[3] or None
        sf8 = len(sf49) > 4 and sf49[4] or None
        sf9 = len(sf49) > 5 and sf49[5] or None
    return {
        "sf4": sf4,
        "sf5": sf5,
        "sf6": sf6,
        "sf7": sf7,
        "sf8": sf8,
        "sf9": sf9,
    }


def reconstruct_reaction_nodes(types, reaction_node):
    new = {}
    for n in types:
        if n % 2 == 1 and types[n] != "reaction":
            new["type"] = types[n]
            new["children"] = [
                {"type": "reaction", "children": reaction_node[x]}
                for x in range(n - 1, n + 1)
            ]
        else:
            new["type"] = types[n]
            new["children"] = reaction_node[n]
    return new


def parse_reaction(reaction_str):
    # parse the reaction string inside parentheses
    charinreaction = "-+/,*. "
    thecontent = pyparsing.Word(pyparsing.alphanums + charinreaction)
    parentheses = pyparsing.nestedExpr("(", ")", content=thecontent)
    free_text = pyparsing.nestedExpr(
        "(", ")", content=thecontent
    ).suppress() + pyparsing.rest_of_line(reaction_str)

    nuclide = re.compile("([0-9]{1,3}-[A-Z0-9]{1,3}-[0-9]{1,3})$")
    process = re.compile("([A-Z0-9]{1,3},[A-Z0-9]{1,4})")
    params = re.compile("([A-Z0-9-+,\/\(\)]*)")

    # parse the reaction string inside parentheses
    a = parentheses.parseString(reaction_str).as_list()
    # parse freetext after reaction string
    b = free_text.parseString(reaction_str)

    reaction_node = {}
    subnode = {}
    node = 0
    types = {}

    for exp in list(flatten(a)):
        if exp.startswith(("/", "*", "-", "+")):
            node += 1
            # reaction_node[node] = subnode
            subnode = {}

            if exp.startswith("/"):
                types[node] = "ratio"

            elif exp.startswith("*"):
                types[node] = "product"

            elif exp.startswith("+"):
                types[node] = "plus"

            elif exp.startswith("-"):
                types[node] = "minus"

        elif nuclide.match(exp):
            if not types.get(node):
                types[node] = "reaction"
            subnode["target"] = nuclide.match(exp).groups()[0]

        elif process.match(exp):
            subnode["process"] = process.match(exp).groups()[0]

        elif params.match(exp):
            subnode.update(split_sfs(params.match(exp).groups()[0].split(",")))
            reaction_node[node] = subnode

    assert len(types) - -len(subnode)

    new = reconstruct_reaction_nodes(types, reaction_node)
    if b:
        new["freetext"] = " ".join(b)
    return new


# test_str = "(92-U-235(N,ABS),,ETA,,MXW) Value = 2.077 prt/reac (test)"
# parse_reaction(test_str)
