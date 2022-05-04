def exfor_iterator(exfor_dic):
    # recursively scan an EXFOR data structure
    # in a top down way
    def recfun(dic):
        if isinstance(dic, dict):
            yield dic
            for key, item in dic.items():
                yield from recfun(item)
    yield from recfun(exfor_dic)

