import sys
import re
import pyparsing
import json
from collections.abc import Iterable
from ..utils.convenience import find_brackets


def parse_reaction(reaction_str):
    reacinfo = {}
    reaction_str = reaction_str[1:-1]
    nuclide = reaction_str[: reaction_str.index("(")]
    reacinfo["target"] = nuclide
    process = reaction_str[reaction_str.index("(") + 1 : reaction_str.index(")")]
    reacinfo["process"] = process
    params = reaction_str[reaction_str.index(")") + 1 :]
    sf49 = params.split(",")
    for i, sf in enumerate(sf49):
        reacinfo["SF" + str(i + 4)] = sf
    return reacinfo


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
