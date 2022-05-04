from exfor_parser import ExforBaseParser

parser = ExforBaseParser()
exfor_entry = parser.readfile('testdata/alldata/entry_33109.txt')
parser.writefile('blabla.txt', exfor_entry)

