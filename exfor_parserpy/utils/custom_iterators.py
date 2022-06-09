############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/05/04
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################

from .convenience import is_dic


def exfor_iterator(exfor_dic):
    """Traverse all subdictionaries bottom-up."""
    if is_dic(exfor_dic):
        for key, item in exfor_dic.items():
            if is_dic(item):
                yield from exfor_iterator(item)
        yield exfor_dic


def exfor_iterator2(exfor_dic, key=None):
    """Traverse all subdictionaries bottom-up."""
    if is_dic(exfor_dic):
        for curkey, item in exfor_dic.items():
            if is_dic(item):
                yield from exfor_iterator2(item, curkey)
        yield key, exfor_dic


def exfor_iterator3(exfor_dic, key=None, parent=None, filterfun=None):
    """Traverse all subdictionaries bottom-up."""
    if is_dic(exfor_dic):
        # we only recurse into elements of the current
        # dictionary if the filterfun applied to it returns False
        if not filterfun or not filterfun(exfor_dic):
            for curkey, item in exfor_dic.items():
                if is_dic(item):
                    yield from exfor_iterator3(item, curkey, exfor_dic, filterfun)
        # in all cases, we return the current dictionary
        # even if filterfun evaluates to True
        yield key, exfor_dic, parent


def search_for_field(dic, fieldname):
    """Find value of field by recursion."""
    for curdic in exfor_iterator(dic):
        if fieldname in curdic:
            return curdic[fieldname]
    return None
