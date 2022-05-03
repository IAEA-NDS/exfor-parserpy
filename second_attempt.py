from exfor_parser import *

with open('testdata/entry_O2098.txt', 'r') as f:
    exfor_content = f.readlines()

exfor_content

resdic, ofs = parse_file(exfor_content)

newlines, ofs = parse_file(None, resdic, inverse=True)

print('\n'.join(newlines))




