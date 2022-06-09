############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/05/04
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################
from .utils.fortran_utils import fortstr2float


def read_str_field(line, pos, width=1, trim=True):
    valstr = line[pos * 11 : (pos + width) * 11]
    # we remove newline and carriage return in any case
    valstr = valstr.rstrip("\n").rstrip("\r")
    return valstr.rstrip() if trim else valstr


def write_str_field(line, pos, mystr, width=1, align="left"):
    line = line.ljust(66)
    newline = line[: pos * 11] if pos > 0 else ""
    if align == "left":
        newline += mystr.ljust(width * 11)
    else:
        newline += mystr.rjust(width * 11)
    newline += line[(pos + width) * 11 :]
    return newline


def read_int_field(line, pos, width=1):
    valstr = read_str_field(line, pos, width)
    return int(valstr)


def write_int_field(line, pos, value, width=1):
    valstr = "{:>11d}".format(value).rjust(width * 11)
    return write_str_field(line, pos, valstr, width)


def read_float_field(line, pos, width=1):
    valstr = read_str_field(line, pos, width)
    return fortstr2float(valstr) if valstr != "" else None


def write_float_field(line, pos, num, width=1):
    if num is not None:
        valstr = "{:11.5g}".format(num).ljust(width * 11)
    else:
        valstr = ""
    return write_str_field(line, pos, valstr, width)


def get_pointer(field):
    return field[11] if field[11] != " " else None


def read_pointered_field(line, pos):
    valstr = read_str_field(line, pos, trim=False)
    pointer = valstr[10] if len(valstr) >= 11 else " "
    fieldkey = valstr[:10].strip()
    return fieldkey, pointer


def write_pointered_field(line, pos, fieldkey, pointer, outkey=True):
    valstr = fieldkey.ljust(10) if outkey else " " * 10
    valstr += pointer[0] if pointer else " "
    return write_str_field(line, pos, valstr)


def write_bib_element(fieldkey, pointer, content, outkey=True):
    content_lines = content.splitlines()
    # we need to append an empty string
    # if a trailing newline exists because
    # splitlines will ignore it
    if content.endswith("\n"):
        content_lines.append("")
    curline = write_pointered_field("", 0, fieldkey, pointer, outkey)
    curline = write_str_field(curline, 1, content_lines[0], width=5)
    newlines = [curline]
    if len(content_lines) > 1:
        for i, curcont in enumerate(content_lines[1:]):
            curline = write_str_field("", 1, curcont, width=5)
            newlines.append(curline)
    return newlines


def read_fields(lines, num, ofs, dtype="str"):
    fields = []
    while num > 0:
        curnum = min(6, num)
        curline = lines[ofs]
        for i in range(curnum):
            if dtype == "strp":
                curfield = read_pointered_field(curline, i)
            elif dtype == "str":
                curfield = read_str_field(curline, i)
            elif dtype == "int":
                curfield = read_int_field(curline, i)
            elif dtype == "float":
                curfield = read_float_field(curline, i)
            else:
                raise TypeError("unknown dtype")
            fields.append(curfield)
        ofs += 1
        num -= curnum
    return fields, ofs


def write_fields(fields, ofs, dtype="str"):
    num = 0
    lines = []
    while num < len(fields):
        curnum = min(6, len(fields) - num)
        curline = ""
        for i in range(curnum):
            curfield = fields[num + i]
            if dtype == "strp":
                curline = write_pointered_field(curline, i, curfield[0], curfield[1])
            elif dtype == "str":
                curline = write_str_field(curline, i, curfield)
            elif dtype == "int":
                curline = write_int_field(curline, i, curfield)
            elif dtype == "float":
                curline = write_float_field(curline, i, curfield)
            else:
                raise TypeError("unknown dtype")
        lines.append(curline)
        num += curnum
    return lines


def update_dic(dic, field, pointer, value, arr=False):
    if not pointer:
        if not arr:
            dic[field] = value
        else:
            dic.setdefault(field, [])
            dic[field].append(value)
    else:
        dic.setdefault(field, {})
        if not arr:
            dic[field][pointer] = value
        else:
            dic[field].setdefault(pointer, [])
            dic[field][pointer].append(value)
    return dic
