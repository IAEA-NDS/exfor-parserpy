############################################################
#
# Author:       Georg Schnabel
# Email:        g.schnabel@iaea.org
# Date:         2022/05/04
# Copyright (c) 2022 International Atomic Energy Agency (IAEA)
# License:      MIT
#
############################################################
from os.path import exists
from .exfor_primitives import (
    read_str_field,
    write_str_field,
    read_pointered_field,
    read_int_field,
    write_int_field,
    read_fields,
    write_fields,
    update_dic,
    write_bib_element,
)
from .utils.convenience import (
    count_fields,
    count_points_in_datablock,
    contains_pointers,
    flatten_default_pointer,
    init_duplicate_field_counters,
    reset_duplicate_field_counters,
    extend_pointer_for_multifield,
)
from .utils.custom_iterators import search_for_field


class ExforBaseParser(object):
    def parse_bib_element(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            pointerdic = {}
            fieldkey, pointer = read_pointered_field(lines[ofs], 0)
            content = read_str_field(lines[ofs], 1, 5)
            ofs += 1
            nextfield, nextpointer = read_pointered_field(lines[ofs], 0)
            while nextfield == "":
                if nextpointer != " ":
                    pointerdic[pointer] = content
                    pointer = nextpointer
                    content = ""
                else:
                    content += "\n"
                content += read_str_field(lines[ofs], 1, 5)
                ofs += 1
                nextfield, nextpointer = read_pointered_field(lines[ofs], 0)
            pointerdic[pointer] = content
            pointerdic = flatten_default_pointer(pointerdic)
            return {fieldkey: pointerdic}, ofs
        # do the inverse transform
        else:
            lines = []
            for fieldkey, content in datadic.items():
                has_pointers = contains_pointers(content)
                if not has_pointers:
                    lines.extend(write_bib_element(fieldkey, None, content))
                else:
                    first = True
                    for pointer in content:
                        lines.extend(
                            write_bib_element(
                                fieldkey, pointer, content[pointer], outkey=first
                            )
                        )
                        first = False
            ofs += len(lines)
            return lines, ofs

    def parse_bib(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            datadic = {}
            if read_str_field(lines[ofs], 0) != "BIB":
                raise TypeError("not a BIB block")
            ofs += 1
            while ofs < len(lines) and read_str_field(lines[ofs], 0) != "ENDBIB":
                field, ofs = self.parse_bib_element(lines, datadic, inverse, ofs)
                datadic.update(field)
            return datadic, ofs
        # inverse transform
        else:
            lines = []
            lines.append(write_str_field("", 0, "BIB"))
            ofs += 1
            for key, value in datadic.items():
                curlines, ofs = self.parse_bib_element(
                    lines, {key: value}, inverse, ofs
                )
                lines.extend(curlines)
            lines.append(write_str_field("", 0, "ENDBIB"))
            ofs += 1
            return lines, ofs

    def parse_common_or_data(
        self, lines=None, datadic=None, inverse=False, ofs=0, what="common"
    ):
        if not inverse:
            datadic = {}
            if read_str_field(lines[ofs], 0) != what.upper():
                raise TypeError(f"not a {what.upper()} block")
            numfields = read_int_field(lines[ofs], 1)
            numlines = read_int_field(lines[ofs], 2) if what == "data" else 1
            ofs += 1

            descrs, ofs = read_fields(lines, numfields, ofs, dtype="strp")
            units, ofs = read_fields(lines, numfields, ofs, dtype="str")
            unit_dic = {}

            counter_dic = init_duplicate_field_counters(descrs)
            for i, (curdescr, pointer) in enumerate(descrs):
                pointer = extend_pointer_for_multifield(curdescr, pointer, counter_dic)
                update_dic(unit_dic, curdescr, pointer, units[i], arr=False)
            for k in unit_dic:
                unit_dic[k] = flatten_default_pointer(unit_dic[k])

            value_dic = {}
            for currow in range(numlines):
                values, ofs = read_fields(lines, numfields, ofs, dtype="float")
                reset_duplicate_field_counters(counter_dic)
                for i, (curdescr, pointer) in enumerate(descrs):
                    pointer = extend_pointer_for_multifield(
                        curdescr, pointer, counter_dic
                    )
                    update_dic(
                        value_dic, curdescr, pointer, values[i], arr=(what == "data")
                    )
            for k in value_dic:
                value_dic[k] = flatten_default_pointer(value_dic[k])

            resdic = {"UNIT": unit_dic, "DATA": value_dic}
            return resdic, ofs
        # inverse transform
        else:
            lines = []
            numfields = count_fields(datadic["DATA"])
            numlines = 1 if what == "common" else count_points_in_datablock(datadic)
            headline = write_str_field("", 0, "COMMON" if what == "common" else "DATA")
            headline = write_int_field(headline, 1, numfields)
            headline = write_int_field(headline, 2, numlines)
            lines.append(headline)
            ofs += 1
            # prepare descrs, unit and value lists
            descrs = []
            units = []
            for fieldkey, cont in datadic["UNIT"].items():
                if contains_pointers(cont):
                    for pointer in cont:
                        descrs.append((fieldkey, pointer))
                        units.append(datadic["UNIT"][fieldkey][pointer])
                else:
                    descrs.append((fieldkey, None))
                    units.append(datadic["UNIT"][fieldkey])
            # write out the header
            curlines = write_fields(descrs, ofs, dtype="strp")
            lines.extend(curlines)
            curlines = write_fields(units, ofs, dtype="str")

            lines.extend(curlines)
            # write the data
            if what == "common":
                values = []
                for fieldkey, cont in datadic["UNIT"].items():
                    if contains_pointers(cont):
                        for pointer in cont:
                            values.append(datadic["DATA"][fieldkey][pointer])
                    else:
                        values.append(datadic["DATA"][fieldkey])
                curlines = write_fields(values, ofs, dtype="float")
                lines.extend(curlines)
                ofs += len(curlines)
            elif what == "data":
                curdic = datadic["DATA"]
                # get a column of the DATA section table
                # to determine the numbe of rows
                while isinstance(curdic, dict):
                    for key, cont in curdic.items():
                        curdic = cont
                        break
                numlines = len(curdic)
                # cycle through the columns
                for currow in range(numlines):
                    values = []
                    for fieldkey, cont in datadic["UNIT"].items():
                        if contains_pointers(cont):
                            for pointer in cont:
                                values.append(
                                    datadic["DATA"][fieldkey][pointer][currow]
                                )
                        else:
                            values.append(datadic["DATA"][fieldkey][currow])
                    curlines = write_fields(values, ofs, dtype="float")
                    lines.extend(curlines)
                    ofs += len(curlines)
            lines.append(
                write_str_field("", 0, "ENDCOMMON" if what == "common" else "ENDDATA")
            )
            ofs += 1
            return lines, ofs

    def parse_subentry(
        self, lines=None, datadic=None, inverse=False, ofs=0, auxinfo=None
    ):
        if not inverse:
            datadic = {}
            if read_str_field(lines[ofs], 0) != "SUBENT":
                raise TypeError("not a SUBENT block")
            if auxinfo is None:
                auxinfo = {}
            auxinfo["subentryid"] = read_str_field(lines[ofs], 1).strip()
            datadic["__entryid"] = auxinfo["entryid"]
            datadic["__subentid"] = auxinfo["subentryid"]
            ofs += 1
            while ofs < len(lines) and read_str_field(lines[ofs], 0) != "ENDSUBENT":
                curfield = read_str_field(lines[ofs], 0)
                if curfield == "BIB":
                    bibsec, ofs = self.parse_bib(lines, datadic, inverse, ofs)
                    datadic["BIB"] = bibsec

                if curfield == "COMMON":
                    commonsec, ofs = self.parse_common_or_data(
                        lines, datadic, inverse, ofs, what="common"
                    )
                    datadic["COMMON"] = commonsec

                if curfield == "DATA":
                    datasec, ofs = self.parse_common_or_data(
                        lines, datadic, inverse, ofs, what="data"
                    )
                    datadic["DATA"] = datasec
                else:
                    ofs += 1
            # advance ofs after ENDSUBENT
            ofs += 1
            return datadic, ofs
        else:
            lines = []
            subent_line = write_str_field("", 0, "SUBENT")
            subent_line = write_str_field(
                subent_line, 1, datadic["__subentid"], align="right"
            )
            lines.append(subent_line)
            ofs += 1
            if "BIB" in datadic:
                curdic = datadic["BIB"]
                curlines, ofs = self.parse_bib(lines, curdic, inverse, ofs)
                lines.extend(curlines)
            if "COMMON" in datadic:
                curdic = datadic["COMMON"]
                curlines, ofs = self.parse_common_or_data(
                    lines, curdic, inverse, ofs, what="common"
                )
                lines.extend(curlines)
            else:
                lines.append(write_str_field("", 0, "NOCOMMON"))
                ofs += 1
            if "DATA" in datadic:
                curdic = datadic["DATA"]
                curlines, ofs = self.parse_common_or_data(
                    lines, curdic, inverse, ofs, what="data"
                )
                lines.extend(curlines)
            lines.append(write_str_field("", 0, "ENDSUBENT"))
            return lines, ofs

    def parse_entry(self, lines=None, datadic=None, inverse=False, ofs=0, auxinfo=None):
        if not inverse:
            datadic = {"subentries": []}
            if read_str_field(lines[ofs], 0) != "ENTRY":
                raise TypeError("not an ENTRY block")
            if auxinfo is None:
                auxinfo = {}
            auxinfo["entryid"] = read_str_field(lines[ofs], 1).strip()
            ofs += 1
            datadic = {}
            while ofs < len(lines) and read_str_field(lines[ofs], 0) != "ENDENTRY":
                if read_str_field(lines[ofs], 0) == "SUBENT":
                    subentid = read_str_field(lines[ofs], 1).strip()
                    subent, ofs = self.parse_subentry(
                        lines, None, inverse, ofs, auxinfo=auxinfo
                    )
                    datadic[subentid] = subent
                else:
                    ofs += 1
            # advance ofs after ENDENTRY line
            ofs += 1
            return datadic, ofs
        else:
            lines = []
            # locate the first subentry id among the subentries
            # in the current entry dictionary and extract the
            # entry id from that
            first_subentid = search_for_field(datadic, "__subentid")
            if not first_subentid:
                raise IndexError("No subentry identification number found")
            entryid = first_subentid[:5]
            entry_line = write_str_field("", 0, "ENTRY")
            entry_line = write_str_field(entry_line, 1, entryid, align="right")
            lines.append(entry_line)
            ofs += 1
            for cursubent, curdic in datadic.items():
                curlines, ofs = self.parse_subentry(lines, curdic, inverse, ofs)
                lines.extend(curlines)
            lines.append(write_str_field("", 0, "ENDENTRY"))
            ofs += 1
            return lines, ofs

    def parse(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            datadic = {}
            while ofs < len(lines):
                if read_str_field(lines[ofs], 0) == "ENTRY":
                    entryid = read_str_field(lines[ofs], 1).strip()
                    entry, ofs = self.parse_entry(lines, None, inverse, ofs)
                    datadic[entryid] = entry
                else:
                    ofs += 1
            return datadic, ofs
        else:
            lines = []
            for curentryid, curdic in datadic.items():
                curlines, ofs = self.parse_entry(lines, curdic, inverse, ofs)
                lines.extend(curlines)
            return lines, ofs

    # the user interface
    def read(self, cont):
        if isinstance(cont, str):
            lines = cont.splitlines()
        elif isinstance(cont, list):
            lines = cont
        else:
            raise TypeError(
                "argument must be either string with "
                + "EXFOR entry or list of lines with EXFOR entry"
            )
        exfor_dic, _ = self.parse(lines=lines)
        return exfor_dic

    def write(self, exfor_dic):
        lines, _ = self.parse(datadic=exfor_dic, inverse=True)
        return lines

    def readfile(self, filename):
        with open(filename, "r") as f:
            cont = f.readlines()
        cont = [line.rstrip("\n").rstrip("\r") for line in cont]
        return self.read(cont)

    def writefile(self, filename, exfor_dic, overwrite=False):
        if not overwrite and exists(filename):
            raise FileExistsError(f"The file {filename} already exists")
        lines = self.write(exfor_dic)
        # lines = [l.rstrip('\n').rstrip('\r') + '\n' for l in lines]
        with open(filename, "w") as f:
            f.writelines(lines)
