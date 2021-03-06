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
    if not is_dic(dic):
        return False
    for k in dic:
        if not is_str(k):
            return False
        # second condition for multifield
        if len(k) != 1 and len(k) != 2:
            return False
        pointer = k[0]
        fieldidx = "" if len(k) == 1 else k[1]
        # check if the pointer is of correct form
        if not (pointer.isalpha() and pointer.isupper()) and not (
            pointer.isdigit() or pointer == " "
        ):
            return False
        # check if multifield index is of correct form if available
        if len(k) == 2 and not fieldidx.isdigit():
            return False
    return True


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
        datablock["DATA"][curkey] = [curval for i in range(numpoints)]


def compare_dictionaries(dic1, dic2, atol=1e-8, rtol=1e-8, info=True):
    def write_info(msg):
        if info:
            print(msg)

    if dic1.keys() != dic2.keys():
        write_info("different number of keys")
        return False
    for k in dic1.keys():
        if isinstance(dic1[k], dict) and isinstance(dic2[k], dict):
            if not compare_dictionaries(dic1[k], dic2[k], atol, rtol, info):
                return False
        elif isinstance(dic1[k], float) and isinstance(dic2[k], float):
            if not abs(dic1[k] - dic2[k]) <= (atol + rtol * abs(dic2[k])):
                write_info(f"number mismatch for {k}")
                return False
        elif isinstance(dic1[k], list) and isinstance(dic2[k], list):
            if len(dic1[k]) != len(dic2[k]):
                write_info(f"length mismatch for {k}")
                return False
            for x, y in zip(dic1[k], dic2[k]):
                if x is not None and y is not None:
                    if abs(x - y) > (atol + rtol * abs(y)):
                        write_info(
                            f"number mismatch of element in list {k} ({x} vs {y})"
                        )
                        return False
                elif (x is None and y is not None) or (x is not None and y is None):
                    write_info(f"None versus non-None for {k}")
                    return False
        elif dic1[k] != dic2[k]:
            write_info(f"difference for {k}")
            return False
    return True


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
