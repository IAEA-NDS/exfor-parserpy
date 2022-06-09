############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/05/19
# Last modified:   2022/05/19
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

# NOTE: Parsing of code blocks can be done smarter than
#       using the regular expression in split_code_and_text
#       below. This should be improved in the future.

from copy import deepcopy
from ..utils.custom_iterators import exfor_iterator3
from ..utils.convenience import is_subentry, contains_pointers
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
                    bibsec.set_default(code_fieldname, {})
                    bibsec.set_default(text_fieldname, {})
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
    m = re.findall(r"\(([^)]+)\)([^(]*)", string)
    code_list = []
    text_list = []
    if not m:
        code_list.append("")
        text_list.append(string)
    else:
        for token in m:
            code = token[0].strip()
            text = token[1].strip()
            code_list.append(code)
            text_list.append(text)
    return code_list, text_list
