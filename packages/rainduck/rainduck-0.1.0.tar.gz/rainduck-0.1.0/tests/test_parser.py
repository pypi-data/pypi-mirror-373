import pytest

from rainduck import errors, tokens


def test_tokenization():
    """Test if result of tokens.tokenize function corresponds with the
    expected.
    """
    code = tokens.tokenize("let a()\n ={<>.,[]+--2_3_b}")
    assert code == [
        tokens.Word("let", 1, 1),
        tokens.Word("a", 1, 5),
        tokens.Char("(", 1, 6),
        tokens.Char(")", 1, 7),
        *[tokens.Char("={<>.,[]+-"[i], 2, 2 + i) for i in range(10)],
        tokens.Number(-23, 2, 12),
        tokens.Word("_b", 2, 16),
        tokens.Char("}", 2, 18),
    ]


simple_code = """let move(from, to) = {from[- -1from to + -1to from]-1from}
copy(from, to, storage) = {from[- -1from to+ -1to storage+ -1storage
from]-1from move(storage, from)
} in
,copy({}, {3>})5{20+.>}
"""


@pytest.mark.parametrize(("index", "char"), [(67, "\\"), (0, "&"), (5, ":")])
def test_unknown_char_error(index, char):
    """Test if exception is raised in tokenization when unknown character found
    and if the exception has correct position of the character.
    """
    index = index % len(simple_code)
    with pytest.raises(errors.RainDuckTokenError) as exc:
        tokens.tokenize(simple_code[:index] + char + simple_code[index + 1 :])
    e = exc.value
    assert e.traceback[0].line_pos == simple_code[:index].count("\n") + 1
    assert e.traceback[0].char_pos == (simple_code[index::-1] + "\n").find("\n")
