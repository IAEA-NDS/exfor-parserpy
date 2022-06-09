############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/05/14
# Last modified:   2022/05/14
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

from copy import deepcopy
from ..utils.custom_iterators import exfor_iterator2
from ..utils.convenience import (
    has_common_block,
    has_data_block,
    count_points_in_datablock,
    merge_common_into_datablock,
)


def uncommonfy(exfor_dic, delete_common=True):
    """Merge COMMON blocks into DATA blocks
    and get rid of them."""
    # we do not want to change in place
    ret_dic = deepcopy(exfor_dic)
    # locate all common blocks
    common_dic = {}
    for curkey, curdic in exfor_iterator2(ret_dic):
        if has_common_block(curdic):
            # we store curdic and ont curdic['COMMON']
            # so that we have a reference to the original
            # common block to easily remove it afterwards
            common_dic[curkey] = curdic
    # merge all the common blocks
    for curkey, curdic in exfor_iterator2(ret_dic):
        if not has_data_block(curdic):
            continue
        # the assumption here is that DATA and COMMON
        # blocks are at the top level of a subentry
        # so we know that curkey contains the subentry accession number.
        datablock = curdic["DATA"]
        numpoints = count_points_in_datablock(datablock)
        # first incorporate the common block of the first subentry.
        # we only match the first 8 characters to be robust
        # against added suffixes due to pointers or similar
        first_subid = curkey[:5] + "001"
        first_subid_ext = first_subid + curkey[8:]
        if first_subid_ext in common_dic:
            first_subid = first_subid_ext

        if first_subid in common_dic:
            commonblock = common_dic[first_subid]["COMMON"]
            merge_common_into_datablock(datablock, commonblock)
        # deal with the common block of the current subentry
        if curkey in common_dic:
            commonblock = common_dic[curkey]["COMMON"]
            merge_common_into_datablock(datablock, commonblock)
    # finally delete all the common blocks if desired
    if delete_common:
        for k, d in common_dic.items():
            del d["COMMON"]

    return ret_dic
