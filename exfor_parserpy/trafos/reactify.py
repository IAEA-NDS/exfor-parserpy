############################################################
#
# Author(s):       Shin Okumura, Georg Schnabel
# Creation date:   2022/08/09
# Last modified:   2022/09/08
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

from copy import deepcopy
from ..utils.convenience import find_brackets, is_subentry, contains_pointers
from ..utils.custom_iterators import exfor_iterator3


def reactify(exfor_dic, reacexpr_field="reaction_expr"):
    ret_dic = deepcopy(exfor_dic)
    outeriter = exfor_iterator3(ret_dic, filterfun=is_subentry)
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
    return ret_dic


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
    # we also add the fields that were omitted at the end of the string
    for i in range(4 + len(sf49), 10):
        reacinfo["SF" + str(i)] = ""
    return reacinfo


def parse_reaction_expression(reaction_str):
    def recfun(reacstr):
        bracket_locs = find_brackets(reacstr, exfor_code_mode=False)

        # we identified a basic reaction string
        if reacstr.strip()[0] != "(":
            reacdic = parse_reaction(reacstr)
            reacdic["type"] = "reaction"
            return reacdic

        # a superfluous bracket pairs are removed like the layers of an onion
        elif len(bracket_locs) == 1:
            return recfun(reacstr[bracket_locs[0][0] + 1 : bracket_locs[0][1]])

        # more bracket pairs indicate operations, such as sums
        elif len(bracket_locs) >= 2:
            # extract the operators
            ops = []
            for i in range(len(bracket_locs) - 1):
                op_start_idx = bracket_locs[i][1] + 1
                op_end_idx = bracket_locs[i + 1][0]
                ops.append(reacstr[op_start_idx:op_end_idx].strip())

            if len(ops) > 1 and ops[0] == "+":
                if not all([x == "+" for x in ops]):
                    raise ValueError("mix of addition with other operators not allowed")

            elif len(ops) > 1 and ops[0] == "*":
                prod_end_pos = len(ops) - 1
                for i in range(len(ops)):
                    if ops[i] != "*":
                        prod_end_pos = i - 1
                        break
                    leftstr = reacstr[: bracket_locs[prod_end_pos][1] + 1]
                    rightstr = reacstr[bracket_locs[prod_end_pos + 1][0] :]
                    terms = []
                    terms.append(recfun(leftstr))
                    terms.append(recfun(rightstr))
                    return {"type": "*", "terms": terms}

            elif any([x == "=" for x in ops]):
                equal_pos = ops.index("=")
                leftstr = reacstr[: bracket_locs[equal_pos][1] + 1]
                rightstr = reacstr[bracket_locs[equal_pos + 1][0] :]
                terms = []
                terms.append(recfun(leftstr))
                terms.append(recfun(rightstr))
                return {"type": "=", "terms": terms}

            elif len(ops) > 1:
                raise ValueError("only single operator allowed")

            # we deal with an arithmetic expression
            terms = []
            for cur_bracket_loc in bracket_locs:
                cont_start = cur_bracket_loc[0] + 1
                cont_end = cur_bracket_loc[1]
                terminfo = recfun(reacstr[cont_start:cont_end])
                terms.append(terminfo)

            return {"type": ops[0], "terms": terms}

    bracket_locs = find_brackets(reaction_str, exfor_code_mode=True)
    if len(bracket_locs) == 0 or bracket_locs[0][0] != 0:
        raise ValueError(
            "an EXFOR reaction field must contain a bracket pair "
            + "and the opening bracket must be at the beginning of the string"
        )
    freetext = reaction_str[bracket_locs[0][1] + 1 :]
    reactree = recfun(reaction_str[bracket_locs[0][0] + 1 : bracket_locs[0][1]])
    return reactree
