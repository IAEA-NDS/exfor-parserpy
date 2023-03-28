############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2023/03/28
# Last modified:   2023/03/28
# License:         MIT
# Copyright (c) 2023 International Atomic Energy Agency (IAEA)
#
############################################################
from os.path import exists
from .exfor_parser import (
    output_entry,
    output_subentry,
    output_bib,
    output_bib_element,
    output_common_or_data,
)
from .exfor_primitives import (
    write_str_field,
    write_int_field,
    write_fields,
    write_bib_element,
)
from .utils.convenience import (
    count_fields,
    count_points_in_datablock,
    contains_pointers,
)
from .utils.custom_iterators import search_for_field


def align_side_by_side(lines1=None, lines2=None):
    if isinstance(lines1, str):
        lines1 = [lines1]
    if isinstance(lines2, str):
        lines2 = [lines2]
    lines1 = lines1.copy() if lines1 is not None else []
    lines2 = lines2.copy() if lines2 is not None else []
    lendiff = len(lines2) - len(lines1)
    if lendiff > 0:
        lines1.extend([" " * 66] * lendiff)
    elif lendiff < 0:
        lines2.extend([" " * 66] * lendiff)
    return [l1 + " | " + l2 for l1, l2 in zip(lines1, lines2)]


def bib_element_diff(datadic1, datadic2):
    if len(datadic1) != 1 or len(datadic2) != 1:
        raise TypeError("dictionary with one element expected")
    fieldkey1 = tuple(datadic1.keys())[0]
    fieldkey2 = tuple(datadic2.keys())[0]
    if fieldkey1 != fieldkey2:
        raise ValueError("mismatching keys")
    fieldkey = fieldkey1
    lines = []

    content1 = datadic1[fieldkey]
    content2 = datadic2[fieldkey]
    if not contains_pointers(content1):
        content1 = {" ": content1}
    if not contains_pointers(content2):
        content2 = {" ": content2}

    pointers = sorted(set(content1).union(content2))
    first1 = True
    first2 = True
    for pointer in pointers:
        if pointer not in content2:
            lines1 = write_bib_element(
                fieldkey, pointer, content1[pointer], outkey=first1
            )
            curlines = align_side_by_side(lines1, None)
            first1 = False
        elif pointer not in content1:
            lines2 = write_bib_element(
                fieldkey, pointer, content2[pointer], outkey=first2
            )
            curlines = align_side_by_side(None, lines2)
            first2 = False
        else:
            lines1 = write_bib_element(
                fieldkey, pointer, content1[pointer], outkey=first1
            )
            lines2 = write_bib_element(
                fieldkey, pointer, content2[pointer], outkey=first2
            )
            lines2 = [li[:11] + "<mark>" + li[11:] + "</mark>" for li in lines2]
            curlines = align_side_by_side(lines1, lines2)
            first1 = False
            first2 = False
        lines.extend(curlines)
    return lines


def bib_diff(datadic1, datadic2):
    lines = []
    start_bib_line = write_str_field("", 0, "BIB")
    lines.append(start_bib_line + " | " + start_bib_line)
    bibkeys = sorted(set(datadic1).union(datadic2))
    for key in bibkeys:
        if key not in datadic2:
            value1 = datadic1[key]
            lines1, _ = output_bib_element({key: value1})
            curlines = align_side_by_side(lines1, None)
        elif key not in datadic1:
            value2 = datadic2[key]
            lines2, _ = output_bib_element({key: value2})
            curlines = align_side_by_side(None, lines2)
        else:
            curdic1 = {key: datadic1[key]}
            curdic2 = {key: datadic2[key]}
            curlines = bib_element_diff(curdic1, curdic2)
        lines.extend(curlines)
    end_bib_field = write_str_field("", 0, "ENDBIB")
    lines.append(end_bib_field + " | " + end_bib_field)
    return lines


def common_or_data_diff(datadic1, datadic2, what="common"):
    lines = []
    numfields1 = count_fields(datadic1["DATA"])
    numlines1 = 1 if what == "common" else count_points_in_datablock(datadic1)
    headline1 = write_str_field("", 0, "COMMON" if what == "common" else "DATA")
    headline1 = write_int_field(headline1, 1, numfields1)
    headline1 = write_int_field(headline1, 2, numlines1)

    numfields2 = count_fields(datadic2["DATA"])
    numlines2 = 1 if what == "common" else count_points_in_datablock(datadic2)
    headline2 = write_str_field("", 0, "COMMON" if what == "common" else "DATA")
    headline2 = write_int_field(headline2, 1, numfields2)
    headline2 = write_int_field(headline2, 2, numlines2)

    curlines = align_side_by_side(headline1, headline2)
    lines.extend(curlines)
    # prepare descrs, unit and value lists
    descrs1 = []
    descrs2 = []
    units1 = []
    units2 = []
    unit_dic1 = datadic1["UNIT"].copy()
    unit_dic2 = datadic2["UNIT"].copy()
    unit_dic1 = {
        k: {" ": v} if not contains_pointers(v) else v for k, v in unit_dic1.items()
    }
    unit_dic2 = {
        k: {" ": v} if not contains_pointers(v) else v for k, v in unit_dic2.items()
    }

    fieldkeys = sorted(set(unit_dic1).union(unit_dic2))
    for fieldkey in fieldkeys:
        if fieldkey not in unit_dic2:
            cont1 = unit_dic1[fieldkey]
            for pointer in cont1:
                descrs1.append((fieldkey, pointer))
                units1.append(cont1[pointer])
        elif fieldkey not in unit_dic1:
            cont2 = unit_dic2[fieldkey]
            for pointer in cont2:
                descrs2.append((fieldkey, pointer))
                units2.append(cont1[pointer])
        else:
            cont1 = unit_dic1[fieldkey]
            cont2 = unit_dic2[fieldkey]
            pointers = sorted(set(unit_dic1[fieldkey]).union(unit_dic2[fieldkey]))
            for pointer in pointers:
                if pointer not in unit_dic2:
                    descrs1.append((fieldkey, pointer))
                    units1.append(cont1[pointer])
                elif pointer not in unit_dic1:
                    descrs2.append((fieldkey, pointer))
                    units2.append(cont1[pointer])
                else:
                    descrs1.append((fieldkey, pointer))
                    units1.append(cont1[pointer])
                    descrs2.append((fieldkey, pointer))
                    units2.append(cont1[pointer])

    # write out the header
    curlines1 = write_fields(descrs1, 0, dtype="strp")
    curlines2 = write_fields(descrs2, 0, dtype="strp")
    curlines = align_side_by_side(curlines1, curlines2)
    lines.extend(curlines)

    curlines1 = write_fields(units1, 0, dtype="str")
    curlines2 = write_fields(units2, 0, dtype="str")
    curlines = align_side_by_side(curlines1, curlines2)
    lines.extend(curlines)

    # write the data
    data_dic1 = datadic1["DATA"].copy()
    data_dic2 = datadic2["DATA"].copy()
    data_dic1 = {
        k: {" ": v} if not contains_pointers(v) else v for k, v in data_dic1.items()
    }
    data_dic2 = {
        k: {" ": v} if not contains_pointers(v) else v for k, v in data_dic2.items()
    }
    if what == "common":
        values1 = []
        values2 = []
        for fieldkey in fieldkeys:
            if fieldkey not in data_dic2:
                cont = data_dic1[fieldkey]
                for pointer in cont:
                    values1.append(cont[pointer])
            elif fieldkey not in data_dic1:
                cont = data_dic2[fieldkey]
                for poiner in cont:
                    values2.append(cont[pointer])
            else:
                cont1 = data_dic1[fieldkey]
                cont2 = data_dic2[fieldkey]
                pointers = sorted(set(cont1).union(cont2))
                for pointer in pointers:
                    if pointer not in cont2:
                        values1.append(cont1[pointer])
                    elif pointer not in cont1:
                        values2.append(cont2[pointer])
                    else:
                        values1.append(cont1[pointer])
                        values2.append(cont2[pointer])

        curlines1 = write_fields(values1, 0, dtype="float")
        curlines2 = write_fields(values2, 0, dtype="float")
        curlines = align_side_by_side(curlines1, curlines2)
        lines.extend(curlines)
    elif what == "data":
        # get a column of the DATA section table
        # to determine the numbe of rows
        curdic1 = data_dic1
        while isinstance(curdic1, dict):
            for key, cont in curdic1.items():
                curdic1 = cont
                break
        numlines1 = len(curdic1)
        curdic2 = data_dic2
        while isinstance(curdic2, dict):
            for key, cont in curdic2.items():
                curdic2 = cont
                break
        numlines2 = len(curdic2)
        # cycle through the columns
        curlines1 = []
        for currow1 in range(numlines1):
            values1 = []
            for fieldkey, cont in unit_dic1.items():
                for pointer in cont:
                    values1.append(data_dic1[fieldkey][pointer][currow1])
            curlines1.extend(write_fields(values1, 0, dtype="float"))

        curlines2 = []
        for currow2 in range(numlines2):
            values2 = []
            for fieldkey, cont in unit_dic2.items():
                for pointer in cont:
                    values2.append(data_dic2[fieldkey][pointer][currow2])
            curlines2.extend(write_fields(values2, 0, dtype="float"))

        curlines = align_side_by_side(curlines1, curlines2)
        lines.extend(curlines)

    end_line = write_str_field("", 0, "ENDCOMMON" if what == "common" else "ENDDATA")
    lines.append(end_line + " | " + end_line)
    return lines


def subentry_diff(datadic1, datadic2):
    lines = []
    subent_line = write_str_field("", 0, "SUBENT")
    subent_line = write_str_field(subent_line, 1, datadic1["__subentid"], align="right")
    lines.append(subent_line + " | " + subent_line)
    if "BIB" in datadic1 and "BIB" in datadic2:
        curdic1 = datadic1["BIB"]
        curdic2 = datadic2["BIB"]
        curlines = bib_diff(curdic1, curdic2)
    elif "BIB" in datadic1:
        curdic1 = datadic1["BIB"]
        lines1, _ = output_bib(curdic1)
        curlines = align_side_by_side(lines1, None)
    elif "BIB" in datadic2:
        curdic2 = datadic2["BIB"]
        lines2, _ = output_bib(curdic2)
        curlines = align_side_by_side(None, lines2)
    else:
        curlines = []
    lines.extend(curlines)

    for blocktype in ("COMMON", "DATA"):
        if blocktype in datadic1 and blocktype in datadic2:
            curdic1 = datadic1[blocktype]
            curdic2 = datadic2[blocktype]
            curlines = common_or_data_diff(curdic1, curdic2, what=blocktype.lower())
        elif blocktype in datadic1:
            curdic1 = datadic1[blocktype]
            lines1, _ = output_common_or_data(curdic1, what=blocktype.lower())
            curlines = align_side_by_side(lines1, None)
        elif blocktype in datadic2:
            curdic2 = datadic2[blocktype]
            lines2, _ = output_common_or_data(curdic2, what=blocktype.lower())
            curlines = align_side_by_side(None, lines2)
        else:
            curlines = []
        lines.extend(curlines)

    end_subent_line = write_str_field("", 0, "ENDSUBENT")
    lines.append(end_subent_line + " | " + end_subent_line)
    return lines


def entry_diff(datadic1, datadic2):
    lines = []
    # locate the first subentry id among the subentries
    # in the current entry dictionary and extract the
    # entry id from that
    first_subentid = search_for_field(datadic1, "__subentid")
    if not first_subentid:
        raise IndexError("No subentry identification number found")
    entryid = first_subentid[:5]

    entry_line = write_str_field("", 0, "ENTRY")
    entry_line = write_str_field(entry_line, 1, entryid, align="right")
    lines.append(entry_line + " | " + entry_line)

    subentids = sorted(set(tuple(datadic1.keys()) + tuple(datadic2.keys())))
    for subentid in subentids:
        if subentid not in datadic2.keys():
            curdic1 = datadic1[subentid]
            lines1, _ = output_subentry(curdic1)
            curlines = align_side_by_side(lines1, None)
        elif subentid not in datadic1.keys():
            curdic2 = datadic2[subentid]
            lines2, _ = output_subentry(curdic2)
            curlines = align_side_by_side(None, lines2)
        else:
            curdic1 = datadic1[subentid]
            curdic2 = datadic2[subentid]
            curlines = subentry_diff(curdic1, curdic2)
        lines.extend(curlines)

    end_entry_line = write_str_field("", 0, "ENDENTRY")
    lines.append(end_entry_line + " | " + end_entry_line)
    return lines


def output_diff(datadic1, datadic2):
    header = []
    header.append("<!DOCTYPE html>")
    header.append("<html>")
    header.append("<head>")
    header.append("<style>")
    header.append("body {")
    header.append("  font-family: 'Courier New', monospace;")
    header.append("}")
    header.append("</style>")
    header.append("</head>")
    header.append("<body>")
    lines = []
    entryids = sorted(set(tuple(datadic1.keys()) + tuple(datadic2.keys())))
    for entryid in entryids:
        if entryid not in datadic2:
            curdic1 = datadic1[entryid]
            lines1, _ = output_entry(curdic1)
            curlines = align_side_by_side(lines1, None)
        elif entryid not in datadic1:
            curdic2 = datadic2[entryid]
            lines2, _ = output_entry(curdic2)
            curlines = align_side_by_side(None, lines2)
        else:
            curdic1 = datadic1[entryid]
            curdic2 = datadic2[entryid]
            curlines = entry_diff(curdic1, curdic2)
        lines.extend(curlines)
    lines = [li.replace(" ", "&nbsp;") for li in lines]
    lines = [li + "<br>" for li in lines]
    lines.append("</body></html>")
    return header + lines


# the user interface
def exfor_diff(exfor_dic1, exfor_dic2):
    lines = output_diff(datadic1=exfor_dic1, datadic2=exfor_dic2)
    return lines


def write_exfor_diff(filename, exfor_dic1, exfor_dic2, overwrite=False):
    if not overwrite and exists(filename):
        raise FileExistsError(f"The file {filename} already exists")
    lines = exfor_diff(exfor_dic1, exfor_dic2)
    with open(filename, "w") as f:
        f.write("\n".join(lines))
