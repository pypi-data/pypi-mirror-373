import pytest

from rainduck.code_elements import (
    BrainFuckLoop,
    BrainFuckOperation,
    CodeBlock,
    Multiplication,
    code_elements,
)
from rainduck.tokens import Char, Number, Word, tokenize


@pytest.mark.parametrize(
    ("code", "element", "rest"),
    [
        (">", BrainFuckOperation, "[,>]"),
        ("[.><]", BrainFuckLoop, "]}"),
        ("-31[9<+]", Multiplication, "5[,]"),
        ("{<2[-,]+++}", CodeBlock, "]-1<>>"),
    ],
)
def test_take(code, element, rest):
    """Test if code element classes takes elements correctly
    and element classes with higher precedence don't take it
    """
    tokenized = tokenize(code + rest)
    tokenized2 = list(tokenized)
    assert isinstance(element.take(tokenized), element)
    rest_tokenized = tokenize(rest)
    assert len(rest_tokenized) == len(tokenized)
    for t1, t2 in zip(rest_tokenized, tokenized):
        match t1, t2:
            case (Char(x), Char(y)) | (Word(x), Word(y)) | (Number(x), Number(y)) if (
                x == y
            ):
                pass
            case _:
                pytest.fail(
                    f"{element.__name__}.take method leaved code {tokenized}, but expected was {rest_tokenized}."
                )
    for elem in code_elements:
        if elem is element:
            break
        tokenized3 = list(tokenized2)
        assert elem.take(tokenized3) is None
        assert tokenized2 == tokenized3
