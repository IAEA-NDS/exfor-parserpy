############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/05/04
# Last modified:   2022/09/07
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################


def apply_factor(data, fact):
    if isinstance(data, list):
        newdata = [d * fact if d is not None else None for d in data]
    else:
        d = data
        newdata = d * fact if d is not None else None
    return newdata


def is_dic(obj):
    return isinstance(obj, dict)


def is_list(obj):
    return isinstance(obj, list)


def is_str(obj):
    return isinstance(obj, str)


def is_subent_id(string, accept_pointer=True):
    if not is_str(string):
        return False
    elif len(string) not in (8, 9):
        return False
    if len(string) == 9 and not accept_pointer:
        return False
    for c in string[:8]:
        if not c.isalpha() and not c.isdigit():
            return False
        elif c.isalpha() and not c.isupper():
            return False
    if len(string) == 9:
        pointer = string[8:]
        if not accept_pointer:
            return False
        elif not is_valid_pointername(pointer, accept_multifield_index=False):
            return False
    return True


def is_subentry(dic, key=None):
    if key is not None and not is_subent_id(key):
        return False
    if "BIB" not in dic:
        return False
    return True


def is_valid_pointername(fieldname, accept_multifield_index=True):
    if not is_str(fieldname):
        return False
    elif len(fieldname) not in (1, 2):
        return False
    # check if the pointer is of correct form
    pointer = fieldname[0]
    if not (pointer.isalpha() and pointer.isupper()) and not (
        pointer.isdigit() or pointer == " "
    ):
        return False
    # check if multifield index is of correct form if available
    if len(fieldname) == 2:
        if not accept_multifield_index:
            return False
        elif not fieldname[1].isdigit():
            return False
    return True


def contains_pointers(dic, accept_pointername_E=True):
    if not is_dic(dic):
        return False
    for k in dic:
        if not is_valid_pointername(k):
            return False
    if "E" in dic and len(dic) == 1 and not accept_pointername_E:
        return False
    return True


def is_multifield_pointer(fieldname):
    if not is_valid_pointername(fieldname):
        return False
    return len(fieldname) == 2


def get_pointername(fieldname):
    return fieldname[0]


def get_multifield_index(fieldname):
    if not is_multifield_pointer(fieldname):
        return None
    else:
        return fieldname[1]


def combine_pointer_and_multifield_index(pointer, index):
    return pointer + index


def flatten_default_pointer(cont):
    if contains_only_default_pointer(cont):
        cont = cont[" "]
    return cont


def contains_only_default_pointer(cont):
    return is_dic(cont) and len(cont) == 1 and " " in cont


def has_common_block(dic):
    if "COMMON" in dic:
        d = dic["COMMON"]
        if "DATA" in d and "UNIT" in d:
            return True
    return False


def has_data_block(dic):
    if "DATA" in dic:
        d = dic["DATA"]
        if not is_dic(d):
            return False
        if "DATA" in d and "UNIT" in d:
            return True
        else:
            return False


def count_fields(dic):
    numfields = 0
    for k, val in dic.items():
        if contains_pointers(val):
            numfields += len(val)
        else:
            numfields += 1
    return numfields


def count_points_in_datablock(datablock):
    length = -1
    errmsg = "Not all lists have the same length " + "in the DATA block"
    for k, arr in datablock["DATA"].items():
        if is_dic(arr):
            # we deal with a pointer
            for p, arr2 in arr.items():
                curlength = len(arr2)
                if length >= 0 and curlength != length:
                    raise IndexError(errmsg)
                length = curlength
        else:
            curlength = len(arr)
            if length >= 0 and curlength != length:
                raise IndexError(msg)
            length = curlength
    return length


def merge_common_into_datablock(datablock, commonblock):
    numpoints = count_points_in_datablock(datablock)
    for curkey, curitem in commonblock["UNIT"].items():
        datablock["UNIT"][curkey] = curitem
    for curkey, curval in commonblock["DATA"].items():
        if not contains_pointers(curval):
            datablock["DATA"][curkey] = [curval for i in range(numpoints)]
        else:
            curdic = {}
            for curpt in curval:
                curval2 = curval[curpt]
                curdic[curpt] = [curval2 for i in range(numpoints)]
            datablock["DATA"][curkey] = curdic


def init_duplicate_field_counters(descrs):
    # determine duplicate descrs, e.g., 2x FLAG, see EXFOR formats manual chap. 4
    dup_dic = {}
    for curdescr_tuple in descrs:
        if curdescr_tuple in dup_dic:
            dup_dic[curdescr_tuple] = True
        else:
            dup_dic[curdescr_tuple] = False
    # only keep the keys associated with duplicated fields
    # and convert them to counter registers
    for k in tuple(dup_dic.keys()):
        if not dup_dic[k]:
            del dup_dic[k]
        else:
            dup_dic[k] = 0
    return dup_dic


def reset_duplicate_field_counters(counter_dic):
    for k in counter_dic:
        counter_dic[k] = 0


def extend_pointer_for_multifield(fieldname, pointer, counter_dic):
    # we extend the pointer string by an additional
    # index for fields that occur multiple times
    # (not necessarily due to pointer)
    curdescr_tuple = (fieldname, pointer)
    ext_pointer = pointer
    if curdescr_tuple in counter_dic:
        ext_pointer += str(counter_dic[curdescr_tuple])
        counter_dic[curdescr_tuple] += 1
    return ext_pointer


def find_brackets(string, exfor_code_mode=True):
    cnt = 0
    in_bracket = False
    start_pos = -1
    is_new_line = True
    bracket_pairs = []
    for curpos, c in enumerate(string):
        allow_open_bracket = is_new_line or not exfor_code_mode
        if c == "(" and (allow_open_bracket or in_bracket):
            cnt += 1
            if not in_bracket:
                start_pos = curpos
                in_bracket = True
        elif c == ")" and in_bracket:
            cnt -= 1
            if cnt == 0:
                in_bracket = False
                bracket_pairs.append((start_pos, curpos))
                startpos = -1
        is_new_line = c == "\n"
    return bracket_pairs
