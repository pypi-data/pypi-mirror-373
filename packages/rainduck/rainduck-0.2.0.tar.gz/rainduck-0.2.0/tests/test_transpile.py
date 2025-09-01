import pytest

from rainduck.transpiler import transpile

bf_codes = ["", "<>+-,.", "+[<>>[[-+]],]..", "[[[]]]", "."]


@pytest.mark.parametrize("code", bf_codes)
def test_bf_to_bf(code):
    """Test if braifuck code traspiles to itself"""
    assert transpile(code) == code


def inversion(code: str):
    return "".join(
        [{"+": "-", "-": "+", "<": ">", ">": "<"}.get(c, c) for c in code[::-1]]
    )


@pytest.mark.parametrize(
    ("first", "rest", "num", "block"),
    [
        (",", "[,]", -3, False),
        ("[[++++]<<<]", "--", 5, False),
        ("[[,],>]", "", 0, False),
        ("<", "[,]", -1, False),
        ("+-.,<>", "+", -2, True),
        ("", "[[-]>]", 7, True),
    ],
)
def test_multiplication(first, rest, num, block):
    """Test if RainDuck multiplication works same as python int * str"""
    transpiled = transpile(str(num) + ("{" + first + "}" if block else first) + rest)
    if num >= 0:
        assert transpiled == num * first + rest
    else:
        assert transpiled == abs(num) * inversion(first) + rest


@pytest.mark.parametrize(
    ("macros", "code"),
    [
        (dict(right=">", r_loop="[right]"), "[,right+r_loop]"),
        (
            dict(left3minus4="<<<----", infinite="[left3minus4++++>>>]"),
            "left3minus4[infinite]",
        ),
        (dict(input="[,]"), "<<input>>"),
    ],
)
def test_macro(macros, code):
    """Test if macros (without arguments) works as expected."""
    code2 = code
    # repeat twice to ensure all macros replaced, even if containing other macros
    for _ in range(2):
        for name, value in macros.items():
            code = code.replace(name, value)
    assert code == transpile(
        "{"
        + f"let {" ".join(name + " = {" + value + "}" for name, value in macros.items())} in {code2}"
        + "}"
    )


@pytest.mark.parametrize(
    ("rainduck", "braifuck"),
    [
        ("let id(x={}) = {x} in id id(2[>])", "[>][>]"),
        ("let a_then_b(a; b) //calls a and then b\n={a b}in a_then_b(b=<; a=>)", "><"),
    ],
)
def test_transpile(rainduck, braifuck):
    assert transpile(rainduck) == braifuck
