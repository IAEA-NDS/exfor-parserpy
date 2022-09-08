import sys
import re
import pyparsing
import json
from collections.abc import Iterable
from ..utils.convenience import find_brackets


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


def parse_reaction(reaction_str):
    subnode = {}
    reaction_str = reaction_str[1:-1]
    nuclide = reaction_str[: reaction_str.index("(")]
    subnode["target"] = nuclide
    process = reaction_str[reaction_str.index("(") + 1 : reaction_str.index(")")]
    subnode["process"] = process
    params = reaction_str[reaction_str.index(")") + 1 :]
    sf49 = params.split(",")
    for i, sf in enumerate(sf49):
        subnode["SF" + str(i + 4)] = sf
    return subnode


def parse_reaction_expression(reaction_str):
    def recfun(reacstr):
        bracket_locs = find_brackets(reacstr, exfor_code_mode=False)
        if reacstr[: bracket_locs[0][0]].strip() != "":
            reacdic = parse_reaction("(" + reacstr + ")")
            reacdic["type"] = "reaction"
            return reacdic

        elif len(bracket_locs) == 2:
            # we deal with an arithmetic expression
            optype = reacstr[bracket_locs[0][1] + 1 : bracket_locs[1][0] - 1].strip()
            childexpr1 = recfun(reacstr[bracket_locs[0][0] + 1 : bracket_locs[0][1]])
            childexpr2 = recfun(reacstr[bracket_locs[1][0] + 1 : bracket_locs[1][1]])
            optypes = {
                "/": "ratio",
                "*": "product",
                "+": "sum",
                "-": "difference",
                "//": "ratio2",
            }
            return {"type": optypes[optype], "terms": [childexpr1, childexpr2]}

        else:
            raise ValueError("invalid reaction string")

    bracket_locs = find_brackets(reaction_str, exfor_code_mode=True)
    if len(bracket_locs) == 0 or bracket_locs[0][0] != 0:
        raise ValueError(
            "an EXFOR reaction field must contain a bracket pair "
            + "and the opening bracket must be at the beginning of the string"
        )
    freetext = reaction_str[bracket_locs[0][1] + 1 :]
    reactree = recfun(reaction_str[bracket_locs[0][0] + 1 : bracket_locs[0][1]])
    return reactree
