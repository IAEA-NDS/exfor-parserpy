import pytest
import sys

sys.path.append("..")
from exfor_parserpy.trafos.extract_reaction import parse_reaction_expression


@pytest.mark.parametrize(
    "test_str",
    (
        (
            "(((94-PU-239(N,F)ELEM/MASS,CUM,FY,,FST)/            (94-PU-239(N,F)42-MO-99,CUM,FY,,FST))//            ((92-U-235(N,F)ELEM/MASS,CUM,FY,,MXW)/            (92-U-235(N,F)42-MO-99,CUM,FY,,MXW)))"
        ),
        ("(92-U-235(N,ABS),,ETA,,MXW) Value = 2.077 prt/reac (test)"),
        (
            "((92-U-235(N,F)ELEM/MASS,CUM,FY,,MXW)/            (92-U-235(N,F)42-MO-99,CUM,FY,,MXW))"
        ),
    ),
)
def test_reaction_parsing(test_str):
    ret = parse_reaction_expression(test_str)
    # TODO: implement test
