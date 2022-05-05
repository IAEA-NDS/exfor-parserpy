import sys
sys.path.append('..')
from exfor_parserpy import ExforBaseParser
from exfor_parserpy.trafos import unitfy

# reading and writing an EXFOR entry
# with pointers
parser = ExforBaseParser()
exfor_entry = parser.readfile('../testdata/entry_21308.txt')
parser.writefile('entry_21308_reproduced.txt', exfor_entry, overwrite=True)

# transform the units present in the EXFOR entry
# all energies to MeV and all cross sections to MB
# also compound quantities are transformed
transformed_entry = unitfy(exfor_entry)
parser.writefile('entry_21308_transformed.txt', transformed_entry, overwrite=True)

# reading and writing an EXFOR entry
# with COMMON field spanning multiple columns
parser = ExforBaseParser()
exfor_entry = parser.readfile('../testdata/entry_O2098.txt')
parser.writefile('entry_O2098_reproduced.txt', exfor_entry, overwrite=True)
transformed_entry = unitfy(exfor_entry)
parser.writefile('entry_O2098_transformed.txt', transformed_entry, overwrite=True)

# reading an EXFOR entry, modifying some information
# and writing it back to a file
parser = ExforBaseParser()
exfor_entry = parser.readfile('../testdata/entry_O2098.txt')
exfor_entry['O2098']['O2098001']['BIB']['AUTHOR'] = 'Some illegal EXFOR here'
parser.writefile('entry_O2098_modified.txt', exfor_entry, overwrite=True)

