############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/05/04
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################
def fortstr2float(valstr, blank=None):
    valstr = valstr.replace(" ", "")
    for i, c in enumerate(valstr):
        if i > 0 and (c == "+" or c == "-"):
            if valstr[i - 1].isdigit() or valstr[i - 1] == ".":
                return float(valstr[:i] + "E" + valstr[i:])
    return float(valstr)


def float2fortstr(val, width=11):
    av = abs(val)
    if av >= 1e-9 and av < 1e10:
        nexp = 1
    elif av >= 1e-99 and av < 1e100:
        nexp = 2
    elif av == 0.0:
        nexp = 1
    else:
        nexp = 3
    ndec = width - nexp - 4
    fmtstr = "{:." + str(ndec) + "E}"
    ss = fmtstr.format(val)
    mantissa, exp = ss.split("E")
    expsign = "+"
    if exp[0] in ("-", "+"):
        expsign = exp[0]
        exp = exp[1:]
    exp = exp[:-1].lstrip("0") + exp[-1]
    numstr = mantissa + expsign + exp
    numstr = numstr.rjust(width)
    assert len(numstr) == width
    return numstr


def read_fort_floats(line, n=6, w=11, blank=None):
    assert isinstance(line, str)
    vals = []
    for i in range(0, n * w, w):
        if line[i : i + w] == " " * w:
            if blank is None:
                raise ValueError("blank encountered but blank=None")
            else:
                vals.append(blank)
        else:
            vals.append(fortstr2float(line[i : i + w]))
    return vals


def write_fort_floats(vals, w=11):
    line = ""
    for i, v in enumerate(vals):
        line += float2fortstr(v, w)
    return line
