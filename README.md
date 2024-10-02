# exfor-parserpy

This parser reads the EXFOR format into a
nested dictionary structure in Python.
Importantly, for the time being it expects to find a
full entry in a file, which means that the file starts
with `ENTRY` and ends with `ENDENTRY`. You can
inspect the files available in the `testdata` directory
to get a better idea of the EXFOR format. The technical
specification of the format is provided in the
[EXFOR formats manual](https://nds.iaea.org/publications/nds/iaea-nds-0207/).
Making the parser smarter to accept files with subentries as top level
organizational unit will be done eventually.

The development of this parser was initiated as a
development project at the IAEA to support the
efforts of WPEC SG50 to design a machine-readable
experimental database. You may also want to follow the
development of a related EXFOR parser published
[here](https://github.com/shinokumura/exforparser).

If you encounter any issues with this parser,
feel free to send an [email](mailto:g.schnabel@iaea.org).
If you want to contribute via a pull request, please
consult the [Contributing](#contributing) section.

## Installation

We recommend the creation of a virtual environment.
For instance, with [venv](https://docs.python.org/3/library/venv.html)
this can be done by
```
python -m venv exfor_venv
```
To activate this environment, if you are on Linux or MacOS, run
```
source ./exfor_venv/bin/activate
```
and on Windows run
```
.\venv\Scripts\activate.bat
```
Now, all packages installed via `pip` will be installed into
the `exfor_venv` folder and are completely isolated from the
user-wide and system-wide installed packages. By runnig
`deactivate`, the virtual environment gets deactivated.

You can install `exfor-paserpy` using pip:
```
pip install git+https://github.com/iaea-nds/exfor-parserpy.git
```

## An example

The `examples` directory contains already an example of how
the parser can be used. We reproduce a part of it here.
Parsing an EXFOR master file can be done by
```
from exfor_parserpy import read_exfor
exfor_dic = read_exfor('testdata/entry_21308.txt')
```
Now we can make manipulations in the EXFOR
dictionary and write it back to a file, for instance:
```
from exfor_parserpy import write_exfor
exfor_dic['21308']['21308001']['BIB']['AUTHOR'] = 'Who is this author?'
write_exfor('testoutput.x4', exfor_dic)
```

Finally, we want to introduce the concept of a *transformer* at the
example of converting all quantities to the same units.
Let's say we want to have all energy units in MeV and all
cross section and derived units in millibarn and write it back
to a file.
This transformer is already included in the package.
```
from exfor_parserpy.trafos import unitfy
transformed_exfor_dic = unitfy(exfor_dic)
write_exfor('trafo_testoutput.x4', transformed_exfor_dic)
```

## Structure of the result of a parse

The organization of the nested dictionary, let's call it `d`,
returned by a parse is as follows:

The keys of the items in `d` are the entry accession numbers, e.g., `21308`.
The item associated with each entry accession number is another
dictionary with the keys given by the accession number extended by the
subentry number, e.g., `21308001` for the first entry.
The items associated with these keys contain the keys `BIB`, `COMMON` (if present)
and `DATA`.
The keys in the `BIB` dictionary reflect the ones in the EXFOR file, e.g.,
`INSTITUTE`, `AUTHOR`, etc.
Both the `COMMON` and `DATA` subdictionary share the same structure.
They contain as keys `UNIT` and `DATA` and the associated items are again dictionaries.
The keys in the `UNIT` item are given by the unit strings present in the EXFOR file,
such as, `EN`, `DATA`, `ERR-S`, etc.
The `DATA` subdictionary has the same keys as the `UNIT` dictionary and the items
are float values in the case of the `COMMON` dictionary and lists of floats in the case of the
`DATA` dictionary.

If a quantity is pointered, e.g., as indicated by `REACTION  1`, the items in the
`UNIT` dictionary are not strings but dictionaries again, whose keys are the pointers
of the EXFOR file. The same applies then to the `DATA` dictionary.

Meta-information, such as in `TITLE` are preserved as strings with line breaks included.
However, in each line blanks at the end of the strings are stripped away.

Here is a tree representing the structure of the nested dictionary:
```
21308 -> 21308001 -> BIB -----> AUTHOR (string)
             |      |
             |      L----> REFERENCE (string)
             |      |
             |      L----> REACTION (string)
             |      |
             |      L----> ...
             |
             |
             L> COMMON --> UNIT ---> ERR-S (string)
             |         |        |
             |         |        |--> DATA (string)
             |         |        |
             |         |        L--> ...
             |         |
             |         L-> DATA ---> ERR-S (float)
             |                  |
             |                  L--> DATA (float)
             |                  |
             |                  L--> ...
             |
             L> DATA ----> UNIT ---> ERR-S (string)
                       |        |
                       |        |--> DATA (string)
                       |        |
                       |        L--> ...
                       |
                       L-> DATA ---> ERR-S (list)
                                |
                                L--> DATA (list)
                                |
                                L--> ...
```

If there are pointers present, e.g., in the `REACTION` field,
we get for that specific field the following structure
(assuming there are two pointers named `1` and `A`):
```
O2098 ->O2098002  -> BIB -----> AUTHOR (string)  -> ...
                     |
                     L----> REFERENCE (string)
                     |
                     L----> REACTION ---> 1 (string)
                     |               |
                     |               L--> A (string)
                     |
                     L----> ...
```

The parser was designed to enable the conversion back from a nested
dictionary to an EXFOR file. This conversion is not perfect
at the moment, e.g., it ignores the `last updated` field in the
head line of the ENTRY and does not set counter variables in
the `COMMON` head line, but apart from that works already pretty well.

## Philosophy of the parser

The parser preserves the logical structure of the EXFOR entry
as much as possible in order to allow for concise code to
convert back to the EXFOR master file.

The guiding principle during the conception of this parser
was to keep the basic parser simple and introduce
transformations to make EXFOR more machine readable
on the parsed output.

We call such functions working on the output of the
parser *transformers*.
A transformer is a function that takes a nested dictionary
resulting from a parse and modifies it in specific ways.
An example of a transformer has already been provided
in the example section above.

## Contributing

If you have made an addition to this package and would like
to contribute it to this project, you may consider performing a
pull request. By effecting a pull request, you accept that
the copyright of your contribution, which is the code or
other information added to this repository, is transferred
to the IAEA. This ensures that we can change the license in
the future if required. We stress that if such a change of
license should ever happen, you can nevertheless continue to
use any version before the switch of license according to the
applicable license at that time.

## Legal note

This code is distributed under the MIT license, see the
accompanying license file for more information.

Copyright (c) International Atomic Energy Agency (IAEA)

