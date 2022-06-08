############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/05/04
# Last modified:   2022/05/15
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


def is_subent_id(string):
    if not is_str(string) and len(string) != 8:
        return False
    for c in string:
        if not c.isalpha() and not c.isdigit():
            return False
        elif c.isalpha() and not c.isupper():
            return False
    return True


def is_subentry(dic, key=None):
    if key is not None and not is_subent_id(key):
        return False
    if "BIB" not in dic:
        return False
    return True


def contains_pointers(dic):
    for k in dic:
        if not is_str(k) or len(k) != 1:
            return False
        elif k.isalpha() and not k.isupper():
            return False
        elif not k.isdigit():
            return False
    return True


def has_common_block(dic):
    if "COMMON" in dic:
        d = dic["COMMON"]
        if "DATA" in d and "UNIT" in d:
            return True
    return False


def has_data_block(dic):
    if "DATA" in dic:
        d = dic["DATA"]
        if "DATA" in d and "UNIT" in d:
            return True
        else:
            return False


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
        datablock["DATA"][curkey] = [curval for i in range(numpoints)]
