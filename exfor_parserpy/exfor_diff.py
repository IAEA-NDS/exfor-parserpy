############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2023/03/28
# Last modified:   2023/03/29
# License:         MIT
# Copyright (c) 2023 International Atomic Energy Agency (IAEA)
#
############################################################
import sys
from os.path import exists
from .exfor_parser import (
    output_entry,
    output_subentry,
    output_bib,
    output_bib_element,
    output_common_or_data,
    read_exfor,
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
import numpy as np
import html


def compute_edit_matrix(str1=None, str2=None, cmpfun=None, cost_sub=100):
    m = np.zeros((len(str1) + 1, len(str2) + 1), dtype=float)
    m[:, 0] = np.arange(m.shape[0])
    m[0, :] = np.arange(m.shape[1])
    for j in range(len(str2)):
        for i in range(len(str1)):
            if cmpfun is None:
                cost = 0.0 if str1[i] == str2[j] else cost_sub
            else:
                cost = cmpfun(str1[i], str2[j])
            m[i + 1, j + 1] = min(m[i, j + 1] + 1.0, m[i + 1, j] + 1.0, m[i, j] + cost)
    return m


def compute_edit_path(str1=None, str2=None, cmpfun=None):
    m = compute_edit_matrix(str1, str2, cmpfun)
    i = m.shape[0] - 1
    j = m.shape[1] - 1
    p = []
    while i > 0 or j > 0:
        cost_before_del = m[i - 1, j]
        cost_before_ins = m[i, j - 1]
        cost_before_sub = m[i - 1, j - 1]
        move_type = np.argmin([cost_before_sub, cost_before_del, cost_before_ins])
        if move_type == 0:
            if cmpfun is None:
                cmpres = 0.0 if str1[i - 1] == str2[j - 1] else 0
            else:
                cmpres = cmpfun(str1[i - 1], str2[j - 1])
            if cmpres == 0:
                p.append("k")
            else:
                p.append("s")
            i -= 1
            j -= 1
        elif move_type == 1:
            i -= 1
            p.append("d")
        else:
            j -= 1
            p.append("i")
    if i > 0:
        p.extend(["d"] * i)
    else:
        p.extend(["i"] * j)
    p.reverse()
    return np.array(p)


def postprocess_edit_type(edit_type, string):
    edit_type = edit_type.copy()
    for i in range(len(edit_type) - 1, 0, -1):
        if edit_type[i] != "i":
            continue
        j = i - 1
        while j >= 0 and edit_type[j] == "i":
            j -= 1
        if j >= 0 and string[i] == string[j]:
            edit_type[i] = "k"
            edit_type[j] = "i"
    return edit_type


def find_last_nonwhite(string):
    i = len(string) - 1
    while i >= 0 and string[i] == " ":
        i -= 1
    return i


def enhanced_escape(string, escape=True):
    if not escape:
        return string
    newstring = html.escape(string)
    newstring = newstring.replace(" ", "&nbsp;")
    return newstring


def add_tablecell_diff_markers(
    lines, mark_mask, start_marker="<mark>", end_marker="</mark>", escape=True
):
    s = "".join(lines)
    fields = [s[i : i + 11] for i in range(0, len(s), 11)]
    lines = []
    curline = ""
    for i, m in enumerate(mark_mask):
        field = fields[i]
        curstr = enhanced_escape(field.rjust(11), escape)
        if m:
            curstr = start_marker + curstr + end_marker
        curline += curstr
        if i % 6 == 5:
            lines.append(curline.ljust(66))
            curline = ""
    need_num = len(mark_mask) % 6
    if need_num != 0:
        curline += enhanced_escape(" " * (11 * (6 - need_num)), escape)
        lines.append(curline)
    return lines


def add_bibfield_diff_markers(
    edit_type_arr,
    string,
    edit_type,
    start_marker="<mark>",
    end_marker="</mark>",
    escape=True,
):
    indel = False
    start_list = []
    term_list = []
    last_nonwhite_idx = find_last_nonwhite(string)
    for i, t, c in zip(range(len(string)), edit_type_arr, string):
        if i > last_nonwhite_idx:
            break
        if t == edit_type and not indel:
            start_list.append(i)
            indel = True
        elif t == "k" and indel:
            term_list.append(i - 1)
            indel = False
    if indel:
        term_list.append(i - 1)

    if len(start_list) == 0:
        return enhanced_escape(string, escape)
    else:
        newstr = enhanced_escape(string[0 : start_list[0]], escape)
        for i, s, t in zip(range(len(start_list)), start_list, term_list):
            partstr = enhanced_escape(string[s : t + 1], escape)
            newstr += start_marker + partstr + end_marker
            if i + 1 < len(start_list):
                next_s = start_list[i + 1]
                newstr += enhanced_escape(string[t + 1 : next_s])
        newstr += enhanced_escape(string[term_list[-1] + 1 :], escape)
        return newstr


def align_side_by_side(
    lines1=None,
    lines2=None,
    escape=True,
    escape_blank=True,
    noline_start_marker='<mark class="noline">',
    noline_end_marker="</mark>",
):
    if isinstance(lines1, str):
        lines1 = [lines1]
    if isinstance(lines2, str):
        lines2 = [lines2]
    lines1 = lines1.copy() if lines1 is not None else []
    lines2 = lines2.copy() if lines2 is not None else []
    if escape:
        lines1 = [enhanced_escape(line) for line in lines1]
        lines2 = [enhanced_escape(line) for line in lines2]
    lendiff = len(lines2) - len(lines1)
    blankline = " " * 66 if not escape_blank else "&nbsp;" * 66
    blankline = noline_start_marker + blankline + noline_end_marker
    if lendiff > 0:
        lines1.extend([blankline] * lendiff)
    elif lendiff < 0:
        lines2.extend([blankline] * (-lendiff))
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
            # diff magic
            lh1 = [enhanced_escape(li[:11]) for li in lines1]
            lc1 = [li[11:] for li in lines1]
            lh2 = [enhanced_escape(li[:11]) for li in lines2]
            lc2 = [li[11:] for li in lines2]
            lens1 = [len(s) for s in lc1]
            lens2 = [len(s) for s in lc2]
            breaks1 = np.cumsum([0] + lens1)
            breaks2 = np.cumsum([0] + lens2)
            lc1j = "".join(lc1)
            lc2j = "".join(lc2)
            edit_path = compute_edit_path(lc1j, lc2j)
            ep1 = edit_path[np.isin(edit_path, ("d", "k"))]
            ep2 = edit_path[np.isin(edit_path, ("i", "k"))]
            ep2 = postprocess_edit_type(ep2, lc2j)
            ep1s = [ep1[i:j] for i, j in zip(breaks1[:-1], breaks1[1:])]
            ep2s = [ep2[i:j] for i, j in zip(breaks2[:-1], breaks2[1:])]
            new_lc1 = []
            for e, line in zip(ep1s, lc1):
                newline = add_bibfield_diff_markers(
                    e,
                    line,
                    "d",
                    start_marker='<mark class="deletion">',
                    end_marker="</mark>",
                )
                new_lc1.append(newline)
            lines1 = [lh + lc for lh, lc in zip(lh1, new_lc1)]

            new_lc2 = []
            for e, line in zip(ep2s, lc2):
                newline = add_bibfield_diff_markers(
                    e,
                    line,
                    "i",
                    start_marker='<mark class="addition">',
                    end_marker="</mark>",
                )
                new_lc2.append(newline)
            lines2 = [lh + lc for lh, lc in zip(lh2, new_lc2)]
            # end diff magic
            curlines = align_side_by_side(
                lines1, lines2, escape=False, escape_blank=True
            )
            first1 = False
            first2 = False
        lines.extend(curlines)
    return lines


def bib_diff(datadic1, datadic2):
    lines = []
    start_bib_line = write_str_field("", 0, "BIB")
    lines.extend(align_side_by_side(start_bib_line, start_bib_line))
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
    lines.extend(align_side_by_side(end_bib_field, end_bib_field))
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

    remove_mask = []
    insert_mask = []
    fieldkeys = sorted(set(unit_dic1).union(unit_dic2))
    for fieldkey in fieldkeys:
        if fieldkey not in unit_dic2:
            cont1 = unit_dic1[fieldkey]
            for pointer in cont1:
                descrs1.append((fieldkey, pointer))
                units1.append(cont1[pointer])
                remove_mask.append(True)
        elif fieldkey not in unit_dic1:
            cont2 = unit_dic2[fieldkey]
            for pointer in cont2:
                descrs2.append((fieldkey, pointer))
                units2.append(cont2[pointer])
                insert_mask.append(True)
        else:
            cont1 = unit_dic1[fieldkey]
            cont2 = unit_dic2[fieldkey]
            pointers = sorted(set(unit_dic1[fieldkey]).union(unit_dic2[fieldkey]))
            for pointer in pointers:
                if pointer not in cont2:
                    descrs1.append((fieldkey, pointer))
                    units1.append(cont1[pointer])
                    remove_mask.append(True)
                elif pointer not in cont1:
                    descrs2.append((fieldkey, pointer))
                    units2.append(cont2[pointer])
                    insert_mask.append(True)
                else:
                    descrs1.append((fieldkey, pointer))
                    units1.append(cont1[pointer])
                    descrs2.append((fieldkey, pointer))
                    units2.append(cont2[pointer])
                    remove_mask.append(False)
                    insert_mask.append(False)

    # write out the header
    remove_mask = np.array(remove_mask, dtype=bool)
    insert_mask = np.array(insert_mask, dtype=bool)

    curlines1 = write_fields(descrs1, 0, dtype="strp")
    curlines1 = add_tablecell_diff_markers(
        curlines1,
        remove_mask,
        start_marker='<mark class="deletion">',
        end_marker="</mark>",
    )
    curlines2 = write_fields(descrs2, 0, dtype="strp")
    curlines2 = add_tablecell_diff_markers(
        curlines2,
        insert_mask,
        start_marker='<mark class="addition">',
        end_marker="</mark>",
    )
    curlines = align_side_by_side(curlines1, curlines2, escape=False)
    lines.extend(curlines)

    curlines1 = write_fields(units1, 0, dtype="str")
    curlines1 = add_tablecell_diff_markers(
        curlines1,
        remove_mask,
        start_marker='<mark class="deletion">',
        end_marker="</mark>",
    )
    curlines2 = write_fields(units2, 0, dtype="str")
    curlines2 = add_tablecell_diff_markers(
        curlines2,
        insert_mask,
        start_marker='<mark class="addition">',
        end_marker="</mark>",
    )
    curlines = align_side_by_side(curlines1, curlines2, escape=False)
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

        cmp_values1 = np.array(values1)[~remove_mask]
        cmp_values2 = np.array(values2)[~insert_mask]
        is_same_value = cmp_values1 == cmp_values2

        ext_mask1 = np.full(len(values1), False)
        ext_mask1[remove_mask] = True
        tmp = np.full(len(is_same_value), False)
        tmp[~is_same_value] = True
        ext_mask1[~remove_mask] = tmp

        ext_mask2 = np.full(len(values2), False)
        ext_mask2[insert_mask] = True
        tmp = np.full(len(is_same_value), False)
        tmp[~is_same_value] = True
        ext_mask2[~insert_mask] = tmp

        curlines1 = write_fields(values1, 0, dtype="float")
        curlines1 = add_tablecell_diff_markers(
            curlines1,
            ext_mask1,
            start_marker='<mark class="deletion">',
            end_marker="</mark>",
        )
        curlines2 = write_fields(values2, 0, dtype="float")
        curlines2 = add_tablecell_diff_markers(
            curlines2,
            ext_mask2,
            start_marker='<mark class="addition">',
            end_marker="</mark>",
        )
        curlines = align_side_by_side(curlines1, curlines2, escape=False)
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
        values1 = []
        for currow1 in range(numlines1):
            values1.append([])
            curvals1 = values1[currow1]
            sorted_keys = sorted(unit_dic1.keys())
            for fieldkey in sorted_keys:
                cont = unit_dic1[fieldkey]
                for pointer in cont:
                    curvals1.append(data_dic1[fieldkey][pointer][currow1])
        values2 = []
        for currow2 in range(numlines2):
            values2.append([])
            curvals2 = values2[currow2]
            sorted_keys = sorted(unit_dic2.keys())
            for fieldkey in sorted_keys:
                cont = unit_dic2[fieldkey]
                for pointer in cont:
                    curvals2.append(data_dic2[fieldkey][pointer][currow2])

        values1_arr = [np.array(v, dtype=float) for v in values1]
        values2_arr = [np.array(v, dtype=float) for v in values2]

        def cmpfun(x, y):
            cmpres = np.sum(x[~remove_mask] != y[~insert_mask])
            cmpres *= 2 / cmpfun.numfields
            return cmpres

        cmpfun.numfields = np.sum(~remove_mask)

        ep = compute_edit_path(values1_arr, values2_arr, cmpfun)
        ep1 = ep[ep != "i"]
        ep2 = ep[ep != "d"]
        numfields1 = len(remove_mask)
        numfields2 = len(insert_mask)
        mask_list1 = [np.full(numfields1, m == "d") for i, m in enumerate(ep1)]
        mask_list2 = [np.full(numfields2, m == "i") for i, m in enumerate(ep2)]
        subidcs1 = np.where(ep1 == "s")[0]
        subidcs2 = np.where(ep2 == "s")[0]
        for i, j in zip(subidcs1, subidcs2):
            v1s = values1_arr[i][~remove_mask]
            v2s = values2_arr[j][~insert_mask]
            tmp = v1s != v2s
            tmp[np.isnan(tmp)] = True
            tmp[np.isnan(v1s) & np.isnan(v2s)] = False
            tmp[np.isnan(tmp)] = False
            mask_list1[i][remove_mask] = True
            mask_list2[j][insert_mask] = True
            mask_list1[i][~remove_mask] = tmp
            mask_list2[j][~insert_mask] = tmp

        curlines1 = []
        curlines2 = []
        idx1 = 0
        idx2 = 0
        noline_start_marker = '<mark class="noline">'
        noline_end_marker = "</mark>"
        empty_line = noline_start_marker + enhanced_escape(" " * 66) + noline_end_marker
        for i, et in enumerate(ep):
            if et != "i":
                vals1 = values1[idx1]
                mask1 = mask_list1[idx1]
                curline1 = write_fields(vals1, 0, dtype="float")
                curline1 = add_tablecell_diff_markers(
                    curline1,
                    mask1,
                    start_marker='<mark class="deletion">',
                    end_marker="</mark>",
                )
                curlines1.extend(curline1)
                idx1 += 1
            else:
                curlines1.append(empty_line)

            if et != "d":
                vals2 = values2[idx2]
                mask2 = mask_list2[idx2]
                curline2 = write_fields(vals2, 0, dtype="float")
                curline2 = add_tablecell_diff_markers(
                    curline2,
                    mask2,
                    start_marker='<mark class="addition">',
                    end_marker="</mark>",
                )
                curlines2.extend(curline2)
                idx2 += 1
            else:
                curlines2.append(empty_line)

        curlines = align_side_by_side(curlines1, curlines2, escape=False)
        lines.extend(curlines)

    end_line = write_str_field("", 0, "ENDCOMMON" if what == "common" else "ENDDATA")
    lines.extend(align_side_by_side(end_line, end_line))
    return lines


def subentry_diff(datadic1, datadic2):
    lines = []
    subent_line = write_str_field("", 0, "SUBENT")
    subent_line = write_str_field(subent_line, 1, datadic1["__subentid"], align="right")
    lines.extend(align_side_by_side(subent_line, subent_line))
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
    lines.extend(align_side_by_side(end_subent_line, end_subent_line))
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
    lines.extend(align_side_by_side(entry_line, entry_line))

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
    lines.extend(align_side_by_side(end_entry_line, end_entry_line))
    return lines


def output_diff(datadic1, datadic2):
    header = [
        """
    <!DOCTYPE html>
    <html> <head>
    <style>
    body { font-family: 'Courier New', monospace; }
    .addition { background-color:#c0ffc8; }
    .deletion { background-color:#ffa07a; }
    .noline { background-color:#ffffe0; }
    </style></head><body>
    """
    ]
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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise TypeError("expecting two filenames with EXFOR entries")
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    exfor_dic1 = read_exfor(filename1)
    exfor_dic2 = read_exfor(filename2)
    diff_lines = exfor_diff(exfor_dic1, exfor_dic2)
    print("\n".join(diff_lines))
