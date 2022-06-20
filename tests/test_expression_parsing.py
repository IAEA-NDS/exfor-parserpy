import pytest
from exfor_parserpy.utils.arithmetic_expr_parsing_new import parse_arithm_expr


def parse_usersym(expr, ofs):
    startofs = ofs
    while ofs < len(expr) and (expr[ofs].isdigit()):
        ofs += 1
    node = {}
    node["type"] = "number"
    node["number"] = float(expr[startofs:ofs])
    return node, ofs


def eval_expr_tree(expr_tree):
    # binary operators
    ntyp = expr_tree["type"]
    if ntyp in ("add", "sub", "prod", "div"):
        leftval = eval_expr_tree(expr_tree["children"][0])
        rightval = eval_expr_tree(expr_tree["children"][1])
        if ntyp == "add":
            return leftval + rightval
        elif ntyp == "sub":
            return leftval - rightval
        elif ntyp == "prod":
            return leftval * rightval
        elif ntyp == "div":
            return leftval / rightval
    # unary operators
    if ntyp in ("neg", "bracket"):
        val = eval_expr_tree(expr_tree["children"][0])
        if ntyp == "neg":
            return -val
        elif ntyp == "bracket":
            return val
    # a value
    if ntyp == "number":
        return expr_tree["number"]


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
    tree, _ = parse_arithm_expr(arithm_expr_str, parse_usersym)
    res = eval_expr_tree(tree)
    assert (
        res == expect_res
    ), f"wrong result {res} for {arithm_expr_str}, expected {expect_res}"
