from pathlib import Path
from exfor_parserpy import read_exfor, write_exfor
from exfor_parserpy.trafos import unitfy, uncommonfy, depointerfy

TEST_DATA = Path(__file__).resolve().parents[1] / "tests" / "testdata"

# reading and writing an EXFOR entry
# with pointers
exfor_entry = read_exfor(TEST_DATA / "entry_21308.txt")
write_exfor("entry_21308_reproduced.txt", exfor_entry, overwrite=True)

# transform the units present in the EXFOR entry
# all energies to MeV and all cross sections to MB
# also compound quantities are transformed
transformed_entry = unitfy(exfor_entry)
write_exfor("entry_21308_transformed.txt", transformed_entry, overwrite=True)

# reading and writing an EXFOR entry
# with COMMON field spanning multiple columns
exfor_entry = read_exfor(TEST_DATA / "entry_O2098.txt")
write_exfor("entry_O2098_reproduced.txt", exfor_entry, overwrite=True)
transformed_entry = unitfy(exfor_entry)
write_exfor("entry_O2098_transformed.txt", transformed_entry, overwrite=True)

# reading an EXFOR entry, modifying some information
# and writing it back to a file
exfor_entry = read_exfor(TEST_DATA / "entry_O2098.txt")
exfor_entry["O2098"]["O2098001"]["BIB"]["AUTHOR"] = "Some illegal EXFOR here"
write_exfor("entry_O2098_modified.txt", exfor_entry, overwrite=True)

# test the uncommonfy transformer with a common field
# in the first subentry
exfor_entry = read_exfor(TEST_DATA / "entry_21308.txt")
transformed_entry = uncommonfy(exfor_entry)
exfor_entry["21308"]["21308002"]["DATA"]["UNIT"]
transformed_entry["21308"]["21308002"]["DATA"]["UNIT"]
exfor_entry["21308"]["21308002"]["DATA"]["DATA"]
transformed_entry["21308"]["21308002"]["DATA"]["DATA"]

# test the uncommonfy transformer with a common field
# in the subentry with the data
exfor_entry = read_exfor(TEST_DATA / "entry_O2098.txt")
transformed_entry = uncommonfy(exfor_entry)
exfor_entry["O2098"]["O2098002"]["DATA"]["UNIT"]
transformed_entry["O2098"]["O2098002"]["DATA"]["UNIT"]
exfor_entry["O2098"]["O2098002"]["DATA"]["DATA"]
transformed_entry["O2098"]["O2098002"]["DATA"]["DATA"]

# test the depointerfy transformer to split up
# subentries with pointers present
exfor_entry = read_exfor(TEST_DATA / "entry_21308.txt")
transformed_entry = depointerfy(exfor_entry)
write_exfor("entry_21308_depointered.txt", transformed_entry, overwrite=True)
