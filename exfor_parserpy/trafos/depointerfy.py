############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/05/15
# Last modified:   2022/05/15
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

from copy import deepcopy
from ..utils.custom_iterators import exfor_iterator2, exfor_iterator3
from ..utils.convenience import contains_pointers, is_subentry


def depointerfy(exfor_dic, delete_pointered_subents=True):
    """Split up subentries with pointers."""
    # we do not want to change in place
    ret_dic = deepcopy(exfor_dic)
    # loop over all subentries present somewhere
    # in the nested dictionary.
    outeriter = exfor_iterator3(ret_dic, filterfun=is_subentry)
    # we expand the iterator as a tuple to force its
    # complete evaluation ahead in time to avoid it
    # getting confused due to inplace changes within the loop
    outeriter = tuple(outeriter)
    for subentid, subent, parent_of_subent in outeriter:
        if not is_subentry(subent, subentid):
            continue
        # collect all the pointers in the current subentry
        pointers = set()
        inneriter = exfor_iterator2(subent)
        for fieldname, fieldcont in inneriter:
            if contains_pointers(fieldcont):
                curpointers = set(fieldcont.keys())
                if len(pointers) != 0 and pointers != curpointers:
                    raise IndexError(f'Inconsistent pointers in subentry {subentid}')
                pointers = curpointers
        # duplicate subentries with pointers
        # and use the values of a specific pointer in each of them.
        for curpointer in pointers:
            newsubent = deepcopy(subent)
            inneriter = tuple(exfor_iterator3(newsubent))
            for fieldname, fieldcont, parent_of_field in inneriter:
                if contains_pointers(fieldcont):
                    parent_of_field[fieldname] = fieldcont[curpointer]
            # construct an extended subentry id
            pointered_subentid = subentid + curpointer
            newsubent['__subentid'] = pointered_subentid
            parent_of_subent[pointered_subentid] = newsubent
        # after all pointers have been processed,
        # delete the old subentry with pointers if desired
        if len(pointers) > 0 and delete_pointered_subents:
            del parent_of_subent[subentid]
    # yay, we are done
    return ret_dic

