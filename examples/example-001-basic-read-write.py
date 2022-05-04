import sys
sys.path.append('..')
from exfor_parser import ExforBaseParser

# reading and writing an EXFOR entry
# with pointers
parser = ExforBaseParser()
exfor_entry = parser.readfile('../testdata/entry_21308.txt')
parser.writefile('entry_21308_reproduced.txt', exfor_entry)
# reading and writing an EXFOR entry
# with COMMON field spanning multiple columns
parser = ExforBaseParser()
exfor_entry = parser.readfile('../testdata/entry_O2098.txt')
parser.writefile('entry_O2098_reproduced.txt', exfor_entry)

