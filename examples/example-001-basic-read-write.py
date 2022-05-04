import sys
sys.path.append('..')
from exfor_parser import ExforBaseParser

parser = ExforBaseParser()
exfor_entry = parser.readfile('../testdata/alldata/entry_33109.txt')
parser.writefile('entry_33109_reproduced.txt', exfor_entry)

