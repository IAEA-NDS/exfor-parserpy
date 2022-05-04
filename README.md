# A prototype of an EXFOR parser

This parser reads the EXFOR format into a
nested dictionary structure in Python.
Importantly, for the time being it expects to find a
full `ENTRY` in a file, which means that the file starts
with 'ENTRY' and ends with `ENDENTRY`. Making the parser
smarter to accept files with subentries as top level
organizational unit should be possible without too much
difficulty if required.

## Structure of the parsed output

The organization of the nested dictionary, let's call it `d`,
returned by a parse is as follows:
The keys of the items in `d` are the entry accession numbers, e.g., `21308`.
The item associated with each entry accession number is another
dictionary with the keys given by the accession number extend by the
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
are float values in the case of the `COMMON` dictionary and lists in the case of the
`DATA` dictionary.

If a quantity is pointered, e.g., as indicated by `REACTION  1`, the items in the
`UNIT` dictionary are not strings, but dictionaries again, whose keys are the pointers
of the EXFOR file. The same applies then to the `DATA` dictionary.

Metainformation, such as in `TITLE` are preserved as strings with linebreaks included.
However, in each line, blanks at the end of the strings are stripped away.

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

If there are pointers present, let's say in the `REACTION` field,
we get for that specific field the following structure
(assuming there is a pointer named `1` and `A`):
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
at the moment (e.g., it ignores the `last updated` field in the
head line of the ENTRY, or does not set counter variables on
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
For an example of a transformer see the next section.

## An example

The `examples` directory contains already an example of how
the parser can be used. We reproduce a part of it here.
Parsing an EXFOR master file can be done by
```
from exfor_parser import ExforBaseParser 
parser = ExforBaseParser()
exfor_dic = parser.readfile('testdata/entry_21308.txt')
```
Now we can make manipulations in the EXFOR
dictionary and write it back to a file, for instance:
```
exfor_dic['21308']['21308001']['BIB']['AUTHOR'] = 'Who is this author?'
parser.writefile('testoutput.x4', exfor_dic)
```

Finally, we want to introduce the concept of a *transformer* at the
example of converting all quantities to the same units.
Let's say we want to have all energy units in MeV and all
cross section and derived units in millibarn and write it back
to a file.
This transformer is already included in the package.
```
from exfor_parser.trafos import unitfy
transformed_exfor_dic = unitfy(exfor_dic)
parser.writefile('trafo_testoutput.x4', transformed_exfor_dic)
```

