def apply_factor(data, fact):
    if isinstance(data, list):
        newdata = [d*fact if d is not None else None for d in data]
    else:
        newdata = d*fact if d is not None else None
    return newdata

