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

