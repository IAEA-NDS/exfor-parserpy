def apply_factor(data, fact):
    if isinstance(data, list):
        newdata = [d*fact if d is not None else None for d in data]
    else:
        d = data
        newdata = d*fact if d is not None else None
    return newdata

def is_dic(obj):
    return isinstance(obj, dict)

def is_list(obj):
    return isinstance(obj, list)

def is_str(obj):
    return isinstance(obj, str)

