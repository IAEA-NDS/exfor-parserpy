import sys
sys.path.append('..')
from exfor_parserpy import ExforBaseParser
from exfor_parserpy.trafos import (unitfy, uncommonfy,
        depointerfy, detextify)
import json


parser = ExforBaseParser()
exfor_entry = parser.readfile('../testdata/entry_21308.txt')

# apply all transformations: unitfy, uncommonfy, depointerfy
trafo_entry = unitfy(exfor_entry)
trafo_entry = uncommonfy(trafo_entry)
trafo_entry = depointerfy(trafo_entry)
parser.writefile('entry_21308_transformed1.txt', trafo_entry, overwrite=True)

# change the order and see if we get identical results
trafo_entry = depointerfy(exfor_entry)
trafo_entry = unitfy(trafo_entry)
trafo_entry = uncommonfy(trafo_entry)
parser.writefile('entry_21308_transformed2.txt', trafo_entry, overwrite=True)


# conversion of compound units in compound quantities
exfor_entry = parser.readfile('../testdata/entry_T0408.txt')
trafo_entry = unitfy(exfor_entry)
parser.writefile('entry_T0408_unitfy.txt', trafo_entry, overwrite=True)

exfor_entry = parser.readfile('../testdata/entry_23245.txt')
trafo_entry = unitfy(exfor_entry)
parser.writefile('entry_23245_unitfy.txt', trafo_entry, overwrite=True)


# example with detextify transformer
exfor_entry = parser.readfile('../testdata/entry_T0408.txt')
trafo_entry = detextify(exfor_entry)
# with detextify we are transforming the EXFOR entry in
# a way that does not allow the conversion back anymore.
# In an EXFOR entry code and free text are by definition
# together in a single string.
#parser.writefile('entry_T0408_detextify.txt', trafo_entry, overwrite=True)
pretty = json.dumps(trafo_entry, indent=4)
print(pretty)

