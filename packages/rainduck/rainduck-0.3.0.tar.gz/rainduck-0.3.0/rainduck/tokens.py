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


@dataclass
class Special:
    name: str
    value: str
    line_pos: int
    char_pos: int


Token = Word | Number | Char | Special


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


def _take_special(
    code: list[str], line_pos: int, char_pos: int
) -> tuple[Special, int, int]:
    start_line_pos = line_pos
    start_char_pos = char_pos
    if not code:
        raise errors.RainDuckSyntaxError(
            "Expected special expression name.", line_pos, char_pos
        )
    name, char_pos = _take_word("", code, line_pos, char_pos)
    value = ""
    if code and code[0] == "(":
        del code[0]
        char_pos += 1
        brackets = 0
        while code:
            c = code.pop(0)
            if c == "\n":
                line_pos += 1
                char_pos = 0
            char_pos += 1
            if c == "(":
                brackets += 1
            elif c == ")" and brackets == 0:
                break
            elif c == ")":
                brackets -= 1
            value += c
    return Special(name.word, value, start_line_pos, start_char_pos), line_pos, char_pos


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
        elif char == "#":
            special, line_pos, char_pos = _take_special(code_list, line_pos, char_pos)
            result.append(special)
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
        elif char == "/" and code_list and code_list[0] == "/":
            if "\n" in code_list:
                del code_list[: code_list.index("\n")]
            else:
                code_list.clear()
        elif not char.isspace():
            result.append(Char(char, line_pos, char_pos))
    return result
