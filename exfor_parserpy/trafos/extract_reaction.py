############################################################
#
# Author(s):       Shin Okumura, Georg Schnabel
# Creation date:   2022/08/09
# Last modified:   2022/09/08
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

from ..utils.convenience import find_brackets, is_subentry, contains_pointers
from ..utils.custom_iterators import exfor_iterator3


def reactify(exfor_dic, reacexpr_field="reaction_expr"):
    outeriter = exfor_iterator3(exfor_dic, filterfun=is_subentry)
    for subentid, subent, parent_of_subent in outeriter:
        if not is_subentry(subent, subentid):
            continue
        if "BIB" not in subent:
            continue
        if "REACTION" not in subent["BIB"]:
            continue
        bibsec = subent["BIB"]
        if not contains_pointers(bibsec["REACTION"]):
            bibsec[reacexpr_field] = parse_reaction_expression(bibsec["REACTION"])
        else:
            bibsec[reacexpr_field] = {}
            for pt, reacstr in bibsec["REACTION"].items():
                bibsec[reacexpr_field][pt] = bibsec[reacexpr_field][
                    pt
                ] = parse_reaction_expression(reacstr)


def parse_reaction(reaction_str):
    reacinfo = {}
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
            reacdic = parse_reaction(reacstr)
            reacdic["type"] = "reaction"
            return reacdic

        elif len(bracket_locs) == 2:
            # we deal with an arithmetic expression
            optype = reacstr[bracket_locs[0][1] + 1 : bracket_locs[1][0] - 1].strip()
            childexpr1 = recfun(reacstr[bracket_locs[0][0] + 1 : bracket_locs[0][1]])
            childexpr2 = recfun(reacstr[bracket_locs[1][0] + 1 : bracket_locs[1][1]])
            return {"type": optype, "terms": [childexpr1, childexpr2]}

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
