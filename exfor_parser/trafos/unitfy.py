from copy import deepcopy
from .auxtools import exfor_iterator
    


    




def apply_factor(data, fact):
    if isinstance(data, list):
        newdata = [d*fact if d is not None else None for d in data]
    else:
        newdata = d*fact if d is not None else None
    return newdata


def change_data_unit(data, unit):
    # xs type units
    if unit.endswith('MB'):
        newunit = 'MB'
        newdata = apply_factor(data, 1)
    elif unit.endswith('B'):
        newunit = 'MB'
        newdata = apply_factor(data, 1e3)
    # inverse xs type units
    # energy type units
    elif unit.endswith('EV'):
        newunit = 'MEV'
        newdata = apply_factor(data, 1e-6)
    elif unit.endswith('KEV'):
        newunit = 'MEV'
        newdata = apply_factor(data, 1e-3)
    elif unit.endswith('MEV'):
        newunit = 'MEV'
        newdata = apply_factor(data, 1)
    elif unit.endswith('GEV'):
        newunit = 'MEV'
        newdata = apply_factor(data, 1e-3)


    return data, newunit



def unitfy(exfor_dic):
    """convert all units to MeV and xs to mbarn"""
    # we do not want to change it in place
    # for the time being
    exfor_dic = deepcopy(exfor_dic)
    for curdic in exfor_iterator:
        # see whether we discovered a table
        # which can be either in a COMMON or
        # DATA block
        if 'UNIT' in curdic: 
            if 'DATA' not in curdic:
                raise TypeError('If UNIT is present, we also expect a 
            energy units 'EV', 'KEV', 'MEV', 'GEV' 
            xs units 'B', 'MB' 




    if 'UNIT' in exfor_dic:
        pass


    if 'COMMON' in exfor_dic:
        pass

def uncommonfy(exfor_dic):
