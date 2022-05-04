from exfor_parser import ExforBaseParser

parser = ExforBaseParser()

exfor_entry = parser.readfile('testdata/alldata/entry_33109.txt')

parser.writefile(exfor_entry, 'blabla.txt')


newlines = parser.write(exfor_entry)

print('\n'.join(newlines))




