import pytest
from exfor_parserpy.utils.arithmetic_expr_parsing_new import (
    parse_arithm_expr,
    eval_expr_tree,
)


def parse_number_str(expr, ofs):
    startofs = ofs
    while ofs < len(expr) and (expr[ofs].isdigit()):
        ofs += 1
    node = {}
    node["type"] = "number"
    node["number"] = float(expr[startofs:ofs])
    return node, ofs


def eval_number_node(expr_tree):
    if expr_tree["type"] == "number":
        return expr_tree["number"]
    else:
        raise TypeError("Invalid node type")


@pytest.mark.parametrize(
    "arithm_expr_str, expect_res",
    (
        ("32 + 64/ 16", 36),
        ("(32+64)/16", 6),
        ("(  32  +  64)/  -16", -6),
        ("32 - -64", 96),
        ("-32 - 64", -96),
        ("  32 * 16 / (32*-16)", -1),
        ("  32 * 16 / 32*-16", -256),
    ),
)
def test_arithmetic_expression_parsing_works_correctly(arithm_expr_str, expect_res):
    tree, _ = parse_arithm_expr(arithm_expr_str, parse_number_str)
    res = eval_expr_tree(tree, eval_number_node)
    assert (
        res == expect_res
    ), f"wrong result {res} for {arithm_expr_str}, expected {expect_res}"
