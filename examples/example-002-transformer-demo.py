from pathlib import Path
from exfor_parserpy import read_exfor, write_exfor
from exfor_parserpy.trafos import unitfy, uncommonfy, depointerfy, detextify, tablify
import json

TEST_DATA = Path(__file__).resolve().parents[1] / "tests" / "testdata"

exfor_entry = read_exfor(TEST_DATA / "entry_21308.txt")

# convert the entry to a table
exfor_table = tablify(exfor_entry)
print(exfor_table)

# apply all transformations: unitfy, uncommonfy, depointerfy
trafo_entry = unitfy(exfor_entry)
trafo_entry = uncommonfy(trafo_entry)
trafo_entry = depointerfy(trafo_entry)
write_exfor("entry_21308_transformed1.txt", trafo_entry, overwrite=True)

# change the order in which the transformer are applied
# and check if we get identical results
trafo_entry = depointerfy(exfor_entry)
trafo_entry = unitfy(trafo_entry)
trafo_entry = uncommonfy(trafo_entry)
write_exfor("entry_21308_transformed2.txt", trafo_entry, overwrite=True)


# conversion of compound units in compound quantities
exfor_entry = read_exfor(TEST_DATA / "entry_T0408.txt")
trafo_entry = unitfy(exfor_entry)
write_exfor("entry_T0408_unitfy.txt", trafo_entry, overwrite=True)

exfor_entry = read_exfor(TEST_DATA / "entry_23245.txt")
trafo_entry = unitfy(exfor_entry)
write_exfor("entry_23245_unitfy.txt", trafo_entry, overwrite=True)

# here we chain transformers before calling
# tablify to create a pandas DataFrame
exfor_table = tablify(unitfy(depointerfy(uncommonfy(exfor_entry))))
print(exfor_table)

# example with detextify transformer
exfor_entry = read_exfor(TEST_DATA / "entry_T0408.txt")
trafo_entry = detextify(exfor_entry)
# with detextify we are transforming the EXFOR entry in
# a way that does not allow the conversion back anymore.
# In an EXFOR entry code and free text are by definition
# together in a single string.
# write_exfor('entry_T0408_detextify.txt', trafo_entry, overwrite=True)
pretty = json.dumps(trafo_entry, indent=4)
print(pretty)
