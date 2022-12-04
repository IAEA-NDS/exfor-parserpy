############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/12/04
# Last modified:   2022/12/04
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################

from copy import deepcopy


def substituty(
    exfor_dic,
    key,
    replace_dict,
    suffix="_description",
    keep_original=True,
    return_copy=True,
    na_value="unknown",
):
    if return_copy:
        exfor_dic = deepcopy(exfor_dic)

    if isinstance(exfor_dic, dict):
        key_list = tuple(exfor_dic)
        for curkey in key_list:
            curel = exfor_dic[curkey]
            if curkey == key and isinstance(curel, str):
                if exfor_dic[key] not in replace_dict:
                    new_value = na_value
                else:
                    new_value = replace_dict[exfor_dic[key]]
                if suffix != "":
                    new_key = key + suffix
                    exfor_dic[new_key] = new_value
                    if not keep_original:
                        del exfor_dic[key]
                else:
                    exfor_dic[key] = new_value
            elif hasattr(curel, "__iter__"):
                substituty(
                    curel,
                    key,
                    replace_dict,
                    suffix=suffix,
                    keep_original=keep_original,
                    return_copy=False,
                    na_value=na_value,
                )

    elif hasattr(exfor_dic, "__iter__") and not isinstance(exfor_dic, str):
        for curel in exfor_dic:
            substituty(
                curel,
                key,
                replace_dict,
                suffix=suffix,
                keep_original=keep_original,
                return_copy=False,
                na_value=na_value,
            )

    return exfor_dic
