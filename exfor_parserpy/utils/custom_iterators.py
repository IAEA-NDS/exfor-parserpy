############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/05/04
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################
def exfor_iterator(exfor_dic):
    # recursively scan an EXFOR data structure
    # in a top down way
    def recfun(dic):
        if isinstance(dic, dict):
            yield dic
            for key, item in dic.items():
                yield from recfun(item)
    yield from recfun(exfor_dic)

