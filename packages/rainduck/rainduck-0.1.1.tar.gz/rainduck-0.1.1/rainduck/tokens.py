from dataclasses import dataclass

from rainduck import errors


@dataclass
class Word:
    word: str
    line_pos: int
    char_pos: int


@dataclass
class Number:
    number: int
    line_pos: int
    char_pos: int


@dataclass
class Char:
    char: str
    line_pos: int
    char_pos: int


Token = Word | Number | Char


def _take_word(
    first: str, rest: list[str], line_pos: int, char_pos: int
) -> tuple[Word, int]:
    """
    Remove characters forming a word (i.e. keyword or macro) from list with
    RainDuck code and return it as a Word instance. Also take position of
    beginning of the word on current line and return position of end, so
    tokenization can continue.
    """
    word = first
    while rest[0].isalnum() or rest[0] == "_":
        word += rest.pop(0)
    return Word(word, line_pos, char_pos), char_pos + len(word) - 1


def _take_num(
    first: str, rest: list[str], line_pos: int, char_pos: int
) -> tuple[Number, int]:
    """
    Remove characters forming a number from beginning of list with
    RainDuck code and return it as a number instance. Also take position of
    beginning of the number on current line and return position of end, so
    tokenization can continue.
    """
    number = first
    while rest[0].isdecimal() or (rest[0] == "_" and rest[1].isdecimal()):
        number += rest.pop(0)
    return Number(int(number), line_pos, char_pos), char_pos + len(number) - 1


def tokenize(code: str) -> list[Token]:
    """Take RainDuck code and return list of tokens."""
    code_list = list(code)
    char_pos = 0
    line_pos = 1
    result: list[Token] = []
    while code_list:
        char_pos += 1
        char = code_list.pop(0)
        if char == "\n":
            char_pos = 0
            line_pos += 1
        elif char.isalpha() or char == "_":
            word, char_pos = _take_word(char, code_list, line_pos, char_pos)
            result.append(word)
        elif char.isdecimal() or (
            char == "-" and code_list and code_list[0].isdecimal()
        ):
            (
                num,
                char_pos,
            ) = _take_num(char, code_list, line_pos, char_pos)
            result.append(num)
        elif not char.isspace():
            result.append(Char(char, line_pos, char_pos))
    return result
