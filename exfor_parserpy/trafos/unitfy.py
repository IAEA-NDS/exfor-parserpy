############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/05/04
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################
from copy import deepcopy
from ..utils import apply_factor, exfor_iterator, is_dic, is_str
from ..utils.arithmetic_expr_parsing import (
    reconstruct_expr_str,
    eval_expr_tree,
    parse_arithm_expr,
)


FACTORS_DIC = {
    # converson factors to obtain MB
    "B": 1e3,
    "MB": 1,
    "MICRO-B": 1e-3,
    "MU-B": 1e-3,
    # conversion factors to obtain MEV
    "MILLI-EV": 1e-9,
    "EV": 1e-6,
    "KEV": 1e-3,
    "MEV": 1,
    "GEV": 1e3,
}

# unit replacement
UNIT_DIC = {
    # xs type units
    "B": "MB",
    "MB": "MB",
    "MICRO-B": "MB",
    # same as MICRO-B but used
    # in differential quantities
    # due to field size limitation
    "MU-B": "MB",
    # energy type units
    "MILLI-EV": "MEV",
    "EV": "MEV",
    "KEV": "MEV",
    "MEV": "MEV",
    "GEV": "MEV",
}


def get_unit_tree(unit_expr_str):
    def parse_unit_str(expr, ofs):
        startofs = ofs
        # the minus sign is included because
        # it appears in unit names such as PER-CENT
        while ofs < len(expr) and (expr[ofs].isalpha() or expr[ofs] == "-"):
            ofs += 1
        node = {}
        node["type"] = "unit"
        node["unit"] = expr[startofs:ofs]
        return node, ofs

    return parse_arithm_expr(unit_expr_str, parse_unit_str)[0]


def substitute_unit_str(unit_tree):
    def subfun(expr_tree):
        if expr_tree["type"] == "unit":
            unitstr = expr_tree["unit"]
            if unitstr in FACTORS_DIC:
                return UNIT_DIC[unitstr]
            else:
                return unitstr
        else:
            raise TypeError("Not a node with a unit")

    return reconstruct_expr_str(unit_tree, subfun)


def compute_conversion_factor(unit_tree):
    def eval_factor(expr_tree):
        if expr_tree["type"] == "unit":
            unitstr = expr_tree["unit"]
            if unitstr in FACTORS_DIC:
                return FACTORS_DIC[unitstr]
            else:
                return 1
        else:
            raise TypeError("Not a node with a unit")

    return eval_expr_tree(unit_tree, eval_factor)


def unitfy(exfor_dic):
    """convert all units to MeV and xs to mbarn

    compound units are also dealt with accordingly"""
    # we do not want to change it in place
    # for the time being
    ret_dic = deepcopy(exfor_dic)
    # go through all dictionaries and identify
    # physics data indicated by the presence of
    # the UNIT and DATA dictionaries
    for curdic in exfor_iterator(ret_dic):
        if "UNIT" in curdic:
            if "DATA" not in curdic:
                raise TypeError("If UNIT is present, we also expect a DATA key")
            for curfield, curunit in curdic["UNIT"].items():
                if is_str(curunit):
                    unit_tree = get_unit_tree(curunit)
                    fact = compute_conversion_factor(unit_tree)
                    newunit = substitute_unit_str(unit_tree)
                    newdata = apply_factor(curdic["DATA"][curfield], fact)
                    curdic["UNIT"][curfield] = newunit
                    curdic["DATA"][curfield] = newdata
                elif is_dic(curunit):
                    # we deal with pointers
                    for curpt, curunit in curunit.items():
                        unit_tree = get_unit_tree(curunit)
                        fact = compute_conversion_factor(unit_tree)
                        newunit = substitute_unit_str(unit_tree)
                        newdata = apply_factor(curdic["DATA"][curfield][curpt], fact)
                        curdic["UNIT"][curfield][curpt] = newunit
                        curdic["DATA"][curfield][curpt] = newdata
                else:
                    raise TypeError(
                        "expected a string or a dictionary in the UNIT field"
                    )
    return ret_dic
