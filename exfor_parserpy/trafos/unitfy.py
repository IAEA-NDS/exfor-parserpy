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
from ..utils import (apply_factor, eval_arithm_expr,
                     exfor_iterator, is_dic, is_str)


FACTORS_DIC = {
    # converson factors to obtain MB
    'B' : 1e3,
    'MB': 1, 
    # conversion factors to obtain MEV
    'MILLI-EV': 1e-9,
    'EV':  1e-6,
    'KEV': 1e-3,
    'MEV': 1,
    'GEV': 1e3
}

# unit replacement
UNIT_DIC = {
    # xs type units
    'B' : 'MB',
    'MB': 'MB',
    # energy type units
    'MILLI-EV': 'MEV',
    'EV' : 'MEV',
    'KEV': 'MEV',
    'MEV': 'MEV',
    'GEV': 'MEV'
}


def unitfy(exfor_dic):
    """convert all units to MeV and xs to mbarn

    compound units are also dealt with accordingly"""
    # we do not want to change it in place
    # for the time being
    ret_dic = deepcopy(exfor_dic)
    # we discard the minus sign as an operator
    # because it appears in EXFOR in symbol names
    # e.g., PER-CENT, ERR-2
    myops = '+*/'
    # go through all dictionaries and identify
    # physics data indicated by the presence of
    # the UNIT and DATA dictionaries
    for curdic in exfor_iterator(ret_dic):
        if 'UNIT' in curdic: 
            if 'DATA' not in curdic:
                raise TypeError('If UNIT is present, we also expect a DATA key')
            for curfield, curunit in curdic['UNIT'].items():
                if is_str(curunit):
                    fact = eval_arithm_expr(curunit, FACTORS_DIC, comp=True, ops=myops)   
                    newunit = eval_arithm_expr(curunit, UNIT_DIC, comp=False, ops=myops)
                    newdata = apply_factor(curdic['DATA'][curfield], fact)
                    curdic['UNIT'][curfield] = newunit
                    curdic['DATA'][curfield] = newdata
                elif is_dic(curunit): 
                    # we deal with pointers
                    for curpt, curunit in curunit.items():
                        fact = eval_arithm_expr(curunit, FACTORS_DIC, comp=True, ops=myops)
                        newunit = eval_arithm_expr(curunit, UNIT_DIC, comp=False, ops=myops)
                        newdata = apply_factor(curdic['DATA'][curfield][curpt], fact)
                        curdic['UNIT'][curfield][curpt] = newunit
                        curdic['DATA'][curfield][curpt] = newdata
                else:
                    raise TypeError('expected a string or a dictionary in the UNIT field')
    return ret_dic

