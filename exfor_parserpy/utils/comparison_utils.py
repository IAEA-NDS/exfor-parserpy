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
