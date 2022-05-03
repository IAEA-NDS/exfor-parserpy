from lark import Lark
from tree_utils import *

exfor_spec = """
// here comes the EBNF (extended Backus Naur form) 
%import common.NEWLINE
%import common.DIGIT
%ignore " "

entry : entry_head entry_body entry_tail
entry_head : "ENTRY" ACCESSION_NUM UPDATE_DATE (/.+/)? NEWLINE
entry_body : subentry*
entry_tail : "ENDENTRY" (/.+/)? NEWLINE
ACCESSION_NUM : (" " | DIGIT)~11
UPDATE_DATE :  (" " | DIGIT)~11

subentry : subent_head subent_body subent_tail 
subent_head : "SUBENT" /.+/ NEWLINE
subent_body : bibsec? commonsec? datasec? 
subent_tail : "ENDSUBENT" /.+/ NEWLINE 

bibsec : bib_head bib_body bib_tail
bib_head : "BIB" /.+/ NEWLINE
bib_body : (BIB_KEY /.+/ NEWLINE)*
bib_tail : "ENDBIB" (/.+/)? NEWLINE
BIB_KEY : "REACTION   " 
        | "MONITOR    " 
        | "INSTITUTE  " 
        | "REFERENCE  " 
        | "AUTHOR     " 
        | "TITLE      " 
        | "STATUS     " 
        | "FACILITY   " 
        | "INC_SOURCE " 
        | "DETECTOR   " 
        | "ERR_ANALYS " 
        | "HISTORY    " 



commonsec : NOCOMMON | (common_head common_body common_tail)
NOCOMMON : "NOCOMMON" (/./)* NEWLINE
common_head : "COMMON" " "~5 FIELD11 FIELD11 /./* NEWLINE
common_body : (FIELD11+ FIELD00? NEWLINE)+
common_tail : "ENDCOMMON" /./* NEWLINE

datasec : data_head data_body data_tail
data_head : "DATA" " "~7 FIELD11 FIELD11 (/./)* NEWLINE
data_body : (FIELD11+ FIELD00? NEWLINE)+ 
data_tail : "ENDDATA" " "~4 FIELD11 (/./)* NEWLINE

FIELD11 : /./~11
// sometimes at the end of the line
// we have an incomplete field with
// less than 11 characters
FIELD00 : /./+
"""

with open('testdata/entry_40641.txt', 'r') as f:
    exfor_cont = f.read()

grammar = Lark(exfor_spec, start='entry')

ch = grammar.parse(exfor_cont)
ch = get_child(ch, 'entry_body')
ch = get_child(ch, 'subentry')
ch = get_child(ch, 'subent_body')
ch = get_child(ch, 'bibsec')
ch = get_child(ch, 'bib_body')
ch = get_child(ch, 'commonsec')
ch = get_child(ch, 'subent_tail')
ch = get_child(ch, 'datasec')
ch = get_child(ch, 'data_body')

get_child_names(ch)
get_child(ch, '__ANON_0')

ch.pretty()



