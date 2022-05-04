from os.path import exists
from .exfor_primitives import (read_str_field, write_str_field,
        read_pointered_field, read_int_field, read_fields, write_fields,
        update_dic, write_bib_element)

class ExforBaseParser(object):

    def parse_bib_element(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            fieldkey, pointer = read_pointered_field(lines[ofs], 0)
            content = read_str_field(lines[ofs], 1, 5)
            ofs += 1
            if not pointer:
                nextfieldkey = read_str_field(lines[ofs], 0)
                while nextfieldkey == '':
                    content += '\n' + read_str_field(lines[ofs], 1, 5)
                    ofs += 1
                    nextfieldkey = read_str_field(lines[ofs], 0)
                return {fieldkey: content}, ofs
            else:
                pointerdic = {}
                nextfield, nextpointer = read_pointered_field(lines[ofs], 0)
                while nextfield == '':
                    if nextfield == '' and nextpointer:
                        pointerdic[pointer] = content
                        pointer = nextpointer
                        content = ''
                    content += read_str_field(lines[ofs], 1, 5)
                    ofs += 1
                    nextfield, nextpointer = read_pointered_field(lines[ofs], 0)
                pointerdic[pointer] = content
                return {fieldkey: pointerdic}, ofs
        # do the inverse transform
        else:
            lines = []
            for fieldkey, content in datadic.items():
                has_pointers = isinstance(content, dict)
                if not has_pointers:
                    lines.extend(write_bib_element(fieldkey, None, content))
                else:
                    for pointer in content:
                        lines.extend(write_bib_element(fieldkey, pointer, content[pointer]))
            ofs += len(lines)
            return lines, ofs

    def parse_bib(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            datadic = {}
            if read_str_field(lines[ofs], 0) != 'BIB':
                raise TypeError('not a BIB block')
            ofs += 1
            while ofs < len(lines) and read_str_field(lines[ofs], 0) != 'ENDBIB':
                field, ofs = self.parse_bib_element(lines, datadic, inverse, ofs)
                datadic.update(field)
            return datadic, ofs
        # inverse transform
        else:
            lines = []
            lines.append(write_str_field('', 0, 'BIB'))
            ofs += 1
            for key, value in datadic.items():
                curlines, ofs = self.parse_bib_element(lines, {key: value}, inverse, ofs)
                lines.extend(curlines)
            lines.append(write_str_field('', 0, 'ENDBIB'))
            ofs += 1
            return lines, ofs

    def parse_common_or_data(self, lines=None, datadic=None, inverse=False, ofs=0,
                             what='common'):
        if not inverse:
            datadic = {}
            if read_str_field(lines[ofs], 0) != what.upper():
                raise TypeError(f'not a {what.upper()} block')
            numfields = read_int_field(lines[ofs], 1)
            numlines = read_int_field(lines[ofs], 2) if what == 'data' else 1
            ofs += 1

            descrs, ofs = read_fields(lines, numfields, ofs, dtype='strp')
            units, ofs = read_fields(lines, numfields, ofs, dtype='str')
            unit_dic = {}
            for i, (curdescr, pointer) in enumerate(descrs):
                update_dic(unit_dic, curdescr, pointer, units[i], arr=False)

            value_dic = {}
            for currow in range(numlines):
                values, ofs = read_fields(lines, numfields, ofs, dtype='float')
                for i, (curdescr, pointer) in enumerate(descrs):
                    update_dic(value_dic, curdescr, pointer, values[i], arr=(what=='data'))

            resdic = {'UNIT': unit_dic, 'DATA': value_dic}
            return resdic, ofs
        # inverse transform
        else:
            lines = []
            lines.append(write_str_field('', 0,
                             'COMMON' if what=='common' else 'DATA'))
            ofs += 1
            # prepare descrs, unit and value lists
            descrs = []
            units = []
            for fieldkey, cont in datadic['UNIT'].items():
                if isinstance(cont, dict):
                    for pointer in cont:
                        descrs.append((fieldkey, pointer))
                        units.append(datadic['UNIT'][fieldkey][pointer])
                else:
                    descrs.append((fieldkey, None))
                    units.append(datadic['UNIT'][fieldkey])
            # write out the header
            curlines = write_fields(descrs, ofs, dtype='strp')
            lines.extend(curlines)
            curlines = write_fields(units, ofs, dtype='str')
            lines.extend(curlines)
            # write the data
            if what == 'common':
                values = []
                for fieldkey, cont in datadic['UNIT'].items():
                    if isinstance(cont, dict):
                        for pointer in cont:
                            values.append(datadic['DATA'][fieldkey][pointer])
                    else:
                        values.append(datadic['DATA'][fieldkey])
                curlines = write_fields(values, ofs, dtype='float')
                lines.extend(curlines)
                ofs += len(curlines)
            elif what == 'data':
                curdic = datadic['DATA']
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
                    for fieldkey, cont in datadic['UNIT'].items():
                        if isinstance(cont, dict):
                            for pointer in cont:
                                values.append(datadic['DATA'][fieldkey][pointer][currow])
                        else:
                            values.append(datadic['DATA'][fieldkey][currow])
                    curlines = write_fields(values, ofs, dtype='float')
                    lines.extend(curlines)
                    ofs += len(curlines)
            lines.append(write_str_field('', 0,
                             'ENDCOMMON' if what=='common' else 'ENDDATA'))
            ofs += 1
            return lines, ofs

    def parse_subentry(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            datadic = {}
            if read_str_field(lines[ofs], 0) != 'SUBENT':
                raise TypeError('not a SUBENT block')
            ofs += 1
            while ofs < len(lines) and read_str_field(lines[ofs], 0) != 'ENDSUBENT':
                curfield = read_str_field(lines[ofs], 0)
                if curfield == 'BIB':
                    bibsec, ofs = self.parse_bib(lines, datadic, inverse, ofs)
                    datadic['BIB'] = bibsec

                if curfield == 'COMMON':
                    commonsec, ofs = self.parse_common_or_data(lines, datadic, inverse, ofs,
                                                          what='common')
                    datadic['COMMON'] = commonsec

                if curfield == 'DATA':
                    datasec, ofs = self.parse_common_or_data(lines, datadic, inverse, ofs,
                                                        what='data')
                    datadic['DATA'] = datasec
                else:
                    ofs += 1
            # advance ofs after ENDSUBENT
            ofs += 1
            return datadic, ofs
        else:
            lines = []
            lines.append(write_str_field('', 0, 'SUBENT'))
            ofs += 1
            if 'BIB' in datadic:
                curdic = datadic['BIB']
                curlines, ofs = self.parse_bib(lines, curdic, inverse, ofs)
                lines.extend(curlines)
            if 'COMMON' in datadic:
                curdic = datadic['COMMON']
                curlines, ofs = self.parse_common_or_data(lines, curdic, inverse, ofs,
                                                     what='common')
                lines.extend(curlines)
            else:
                lines.append(write_str_field('', 0, 'NOCOMMON'))
                ofs += 1
            if 'DATA' in datadic:
                curdic = datadic['DATA']
                curlines, ofs = self.parse_common_or_data(lines, curdic, inverse, ofs,
                                                     what='data')
                lines.extend(curlines)
            lines.append(write_str_field('', 0, 'ENDSUBENT'))
            return lines, ofs

    def parse_entry(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            datadic = {'subentries': []}
            if read_str_field(lines[ofs], 0) != 'ENTRY':
                raise TypeError('not an ENTRY block')
            ofs += 1
            datadic['subentries'] = []
            while ofs < len(lines) and read_str_field(lines[ofs], 0) != 'ENDENTRY':
                if read_str_field(lines[ofs], 0) == 'SUBENT':
                    subent, ofs = self.parse_subentry(lines, None, inverse, ofs)
                    datadic['subentries'].append(subent)
                else:
                    ofs += 1
            # advance ofs after ENDENTRY line
            ofs += 1
            return datadic, ofs
        else:
            lines = []
            lines.append(write_str_field('', 0, 'ENTRY'))
            ofs += 1
            for curdic in datadic['subentries']:
                curlines, ofs = self.parse_subentry(lines, curdic, inverse, ofs)
                lines.extend(curlines)
            lines.append(write_str_field('', 0, 'ENDENTRY'))
            ofs += 1
            return lines, ofs

    def parse(self, lines=None, datadic=None, inverse=False, ofs=0):
        if not inverse:
            datadic = {}
            while ofs < len(lines):
                if read_str_field(lines[ofs], 0) == 'ENTRY':
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
            raise TypeError('argument must be either string with ' +
                            'EXFOR entry or list of lines with EXFOR entry')
        exfor_dic, _ = self.parse(lines=lines)
        return exfor_dic

    def write(self, exfor_dic):
        lines, _ = self.parse(datadic=exfor_dic, inverse=True)
        return lines

    def readfile(self, filename):
        with open(filename, 'r') as f:
            cont = f.readlines()
        return self.read(cont)

    def writefile(self, filename, exfor_dic):
        if exists(filename):
            raise FileExistsError(f'The file {filename} already exists')
        lines = self.write(exfor_dic)
        lines = [l.rstrip('\n').rstrip('\r') + '\n' for l in lines]
        with open(filename, 'w') as f:
            f.writelines(lines)

