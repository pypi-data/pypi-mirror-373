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
