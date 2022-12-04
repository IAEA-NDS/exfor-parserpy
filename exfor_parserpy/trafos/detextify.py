############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/05/19
# Last modified:   2022/09/07
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

from copy import deepcopy
from ..utils.custom_iterators import exfor_iterator3
from ..utils.convenience import is_subentry, contains_pointers, find_brackets
import re


def detextify(exfor_dic, keep_original_field=False):
    """Strip the text from the bibliographic fields."""
    ret_dic = deepcopy(exfor_dic)
    outeriter = exfor_iterator3(ret_dic, filterfun=is_subentry)
    for subentid, subent, parent_of_subent in outeriter:
        if not is_subentry(subent, subentid):
            continue
        if "BIB" not in subent:
            continue
        bibsec = subent["BIB"]
        # the tupling is done because otherwise the
        # iterator complains about changes to the dictionary
        for fieldname, fieldcont in tuple(bibsec.items()):
            # we skip for the time being the splitting
            # of the REACTION field due to the increased
            # complexity of the "reaction algebra"
            if fieldname == "REACTION":
                continue
            code_fieldname = fieldname + "_codes"
            text_fieldname = fieldname + "_texts"
            if contains_pointers(fieldcont):
                for curpointer, fieldcont2 in fieldcont.items():
                    code_list, text_list = split_code_and_text(fieldcont2)
                    bibsec.setdefault(code_fieldname, {})
                    bibsec.setdefault(text_fieldname, {})
                    bibsec[code_fieldname][curpointer] = code_list
                    bibsec[text_fieldname][curpointer] = text_list
            else:
                code_list, text_list = split_code_and_text(fieldcont)
                bibsec[code_fieldname] = code_list
                bibsec[text_fieldname] = text_list
            if not keep_original_field:
                del bibsec[fieldname]
    return ret_dic


def split_code_and_text(string):
    # strategy: if there isn't an opening bracket
    # in the first position, the field contains free
    # text only. Otherwise the field contains one
    # or more codes in a bracket pair potentially
    # followed by free text. A field can contain
    # codes in several brackets but then each
    # bracket pair must start on a new line.
    code_list = []
    text_list = []
    code_locations = find_brackets(string)
    if len(code_locations) == 0:
        code_list = [""]
        text_list = string
    else:
        for i, (start, stop) in enumerate(code_locations):
            curcode = string[start + 1 : stop]
            curcode = curcode.replace("\n", "").replace("\r", "")
            code_list.append(curcode)
            if len(code_locations) > i + 1:
                next_pos = code_locations[i + 1][0]
            else:
                next_pos = len(string)
            curtext = string[stop + 1 : next_pos]
            text_list.append(curtext)
    return code_list, text_list
