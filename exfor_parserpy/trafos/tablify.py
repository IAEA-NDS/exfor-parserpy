############################################################
#
# Author(s):       Georg Schnabel
# Email:           g.schnabel@iaea.org
# Creation date:   2022/09/04
# Last modified:   2022/09/05
# License:         MIT
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
#
############################################################
import pandas as pd
import numpy as np
import re
from ..utils.convenience import is_dic, contains_pointers, is_subentry
from ..utils.custom_iterators import exfor_iterator3


def tablify(exfor_dic, sep=".", pointersep="#", keep_toplevel=False):
    """Convert EXFOR entry to table."""
    # first traverse the nested dictionary and locate
    # all the subentries. Retrieve tuples of column
    # names and content from them.
    df_list = []
    outeriter = exfor_iterator3(exfor_dic, filterfun=is_subentry)
    for subentid, subent, parent_of_subent in outeriter:
        if not is_subentry(subent, subentid):
            continue
        cur_table_dic = {}
        coliter = column_iterator(subent, sep=sep, pointersep=pointersep)
        for col, cont in coliter:
            tcol, tcont = column_transformer(col, cont, sep, pointersep, keep_toplevel)
            if tcol is not None:
                cur_table_dic[tcol] = tcont
        try:
            curdf = pd.DataFrame.from_dict(cur_table_dic)
        except ValueError:
            # if all fields in cur_table_dic are scalars
            # the above instruction will fail and we need
            # to do it like this:
            curdf = pd.DataFrame([cur_table_dic])
        df_list.append(curdf)

    df = pd.concat(df_list, ignore_index=True)
    # merge the information of the first subentry into all
    # subsequent subentries and remove the rows related
    # to the first subentry from the dataframe
    df_list = []
    df["auxgroup"] = df.SUBENTRY.str.slice(5, 8)
    first_subent_df = df[df.auxgroup == "001"].drop("auxgroup", axis=1)
    other_subent_df = df[df.auxgroup != "001"].drop("auxgroup", axis=1)
    other_subent_df.set_index(["ENTRY", "SUBENTRY"], inplace=True)
    first_subent_df.set_index(["ENTRY", "SUBENTRY"], inplace=True)

    entry_groups = other_subent_df.groupby(by=["ENTRY"])
    for cur_group in entry_groups:
        curdf = cur_group[1].dropna(axis=1, how="all")
        curdf.reset_index(inplace=True)
        try:
            firstsub = first_subent_df.loc[cur_group[0]].copy()
            firstsub.dropna(axis=1, inplace=True)
            nrep = len(curdf) / len(firstsub)
            firstsub = pd.DataFrame(
                np.repeat(firstsub.values, nrep, axis=0), columns=firstsub.columns
            )
            curdf = pd.concat([firstsub, curdf], axis=1)
        except KeyError:
            # we did not find a corresponding first subentry
            # so nothing to do as curdf is already assigned
            pass
        df_list.append(curdf)

    ret_df = pd.concat(df_list, axis=0, ignore_index=True)
    # move entry and subentry column to front
    first_cols = ["ENTRY", "SUBENTRY"]
    ret_df = ret_df[first_cols + [x for x in ret_df.columns if x not in first_cols]]
    return ret_df


def column_iterator(elem, path=None, sep=".", pointersep="#"):
    # NOTE: the contains_pointers function indicates true if there are
    # only keys consisting of a single letter. In the DATA and
    # COMMON subdictionary this heuristic can fail if there is
    # only one quantity present which is the outgoing energy indicated by E.
    # Therefore we special case this possibility.
    no_pointer = False
    if path is not None and len(path) >= 2:
        no_pointer = path[-2:] in (
            ("DATA", "DATA"),
            ("DATA", "UNIT"),
            ("COMMON", "DATA"),
            ("COMMON", "UNIT"),
        )
    # there can be the case DATA/DATA/DATA, in other words
    # a DATA field in the DATA table of the DATA section.
    # here pointers may occur and we need to reverse the
    # heuristic above.
    if path is not None and len(path) >= 3 and path[-3:] == ("DATA", "DATA", "DATA"):
        no_pointer = False

    has_pointers = contains_pointers(elem) and not no_pointer
    if is_dic(elem) and not has_pointers:
        for key, item in elem.items():
            if path is None:
                curpath = (key,)
            else:
                curpath = path + (key,)
            yield from column_iterator(item, curpath, sep, pointersep)
    elif has_pointers:
        for key, item in elem.items():
            pathstr = sep.join(path) + pointersep + key
            yield pathstr, item
    else:
        pathstr = sep.join(path)
        yield pathstr, elem


def column_transformer(colname, content, sep, pointersep, keep_toplevel=False):
    path = colname.split(sep)
    if "BIB" in path:
        startpos = path.index("BIB")
        if not keep_toplevel:
            startpos += 1
        path = sep.join(path[startpos:])
        return path, content

    elif "COMMON" in path:
        startpos = path.index("COMMON")
        if path[startpos + 1] == "UNIT":
            return None, content
        elif path[startpos + 1] == "DATA":
            path = path[: startpos + 1] + path[startpos + 2 :]
            if not keep_toplevel:
                startpos += 1
            path = sep.join(path[startpos:])
            return path, content

    elif "DATA" in path:
        startpos = path.index("DATA")
        if path[startpos + 1] == "DATA":
            if not keep_toplevel:
                startpos += 1
            path = sep.join(path[startpos + 1 :])
            return path, content
        elif path[startpos + 1] == "UNIT":
            return None, content

    elif path[-1] == "__entryid":
        return "ENTRY", content

    elif path[-1] == "__subentid":
        return "SUBENTRY", content

    return colname, content
