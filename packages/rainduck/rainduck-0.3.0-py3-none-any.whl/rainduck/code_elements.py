from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from pathlib import Path
from typing import Any, Self, Sequence, cast

from rainduck.errors import (
    RainDuckArgumentError,
    RainDuckError,
    RainDuckImportError,
    RainDuckInversionError,
    RainDuckNameError,
    RainDuckSyntaxError,
)
from rainduck.tokens import Char, Number, Special, Token, Word


class _CodeElementMeta(ABCMeta):

    precedence: float = 0
    assign_to_list: bool

    def __init__(cls, name: str, bases: tuple[type], namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        if namespace.get("assign_to_list", True):
            for i in range(len(code_elements)):
                if code_elements[i].precedence >= cls.precedence:
                    code_elements.insert(i, cls)
                    break
            else:
                code_elements.append(cls)

    def take(
        cls,
        code: list[Token],
        parent: "CodeBlock | None" = None,
        file_path: Path | None = None,
    ) -> "CodeElement | None":
        pass


code_elements: list[_CodeElementMeta] = []


class CodeElement(metaclass=_CodeElementMeta):

    assign_to_list = False

    @abstractmethod
    def transpile(self, inverse: bool = False) -> list["BrainFuck"]:
        pass


class BrainFuck(CodeElement):
    assign_to_list = False

    @abstractmethod
    def __str__(self) -> str:
        pass


class BrainFuckOperation(BrainFuck):

    code: str

    def __init__(self, code: str) -> None:
        self.code = code

    @classmethod
    def take(
        cls,
        code: list[Token],
        parent: "CodeBlock | None" = None,
        file_path: Path | None = None,
    ) -> Self | None:
        fst = code[0]
        match fst:
            case Char(c) if c in "<>+-,.":
                del code[0]
                return cls(c)
        return None

    def transpile(self, inverse: bool = False) -> list["BrainFuck"]:
        return [
            BrainFuckOperation(
                {"+": "-", "-": "+", "<": ">", ">": "<"}.get(self.code, self.code)
                if inverse
                else self.code
            )
        ]

    def __str__(self) -> str:
        return self.code


class BrainFuckLoop(BrainFuck):

    code: Sequence[CodeElement]
    line_pos: int | None
    char_pos: int | None

    def __init__(
        self, code: Sequence[CodeElement], line_pos: int | None, char_pos: int | None
    ):
        self.code = code
        self.line_pos = line_pos
        self.char_pos = char_pos

    @classmethod
    def take(
        cls,
        tokens: list[Token],
        parent: "CodeBlock | None" = None,
        file_path: Path | None = None,
    ) -> Self | None:
        match tokens[0]:
            case Char("[", line_pos, char_pos):
                del tokens[0]
                brackets = 0
                code: list[Token] = []
                while tokens:
                    match tokens.pop(0), brackets:
                        case Char("[") as t, _:
                            brackets += 1
                            code.append(t)
                        case Char("]"), 0:
                            break
                        case Char("]") as t, _:
                            brackets -= 1
                            code.append(t)
                        case t, _:
                            code.append(t)
                else:
                    raise RainDuckSyntaxError("Missing ']'", line_pos, char_pos)
                return cls(parse_list(code, parent, file_path), line_pos, char_pos)
        return None

    def transpile(self, inverse: bool = False) -> list["BrainFuck"]:
        if inverse:
            raise RainDuckInversionError(
                "Loop can't be inverted", self.line_pos, self.char_pos
            )
        return [
            BrainFuckLoop(
                sum([x.transpile() for x in self.code], []),
                self.line_pos,
                self.char_pos,
            )
        ]

    def __str__(self) -> str:
        return "[" + "".join(str(x) for x in self.code) + "]"


class Multiplication(CodeElement):

    num: int
    code: CodeElement
    line_pos: int | None
    char_pos: int | None

    def __init__(
        self, num: int, code: CodeElement, line_pos: int | None, char_pos: int | None
    ) -> None:
        self.num = num
        self.code = code
        self.line_pos = line_pos
        self.char_pos = char_pos

    @classmethod
    def take(
        cls,
        code: list[Token],
        parent: "CodeBlock | None" = None,
        file_path: Path | None = None,
    ) -> "CodeElement | None":
        match code[0]:
            case Number(n, line_pos, char_pos):
                del code[0]
                return cls(n, _take_elem(code, parent, file_path), line_pos, char_pos)
        return None

    def transpile(self, inverse: bool = False) -> list["BrainFuck"]:
        inv = (self.num >= 0) == inverse
        num = abs(self.num)
        if inverse:
            try:
                return num * self.code.transpile(inv)
            except RainDuckInversionError as e:
                e.add_pointer(self.line_pos, self.char_pos)
                raise e
        else:
            return num * self.code.transpile(inv)


class Macro:

    name: str
    args: OrderedDict[str, CodeElement | None]
    code: CodeElement

    def __init__(
        self, name: str, args: OrderedDict[str, CodeElement | None], code: CodeElement
    ):
        assert isinstance(code, CodeBlock) or not args
        self.name = name
        self.args = args
        self.code = code

    def __call__(self, *args: CodeElement, **kwds: CodeElement) -> CodeElement:
        if len(self.args) < len(args):
            raise RainDuckArgumentError(
                f"Too many arguments for macro {self.name} (max {len(self.args)} expected, {len(args)} given)"
            )
        code = self.code
        if args or self.args:
            if not self.args and isinstance(self.code, CodeBlock):
                raise RainDuckArgumentError(f"Macro '{self.name}' takes no arguments.")
            arguments = {}
            for name, value in zip(self.args, args):
                arguments[name] = value
            for name, value in kwds.items():
                if name not in self.args:
                    raise RainDuckArgumentError(
                        f"Macro '{self.name}' got an unexpected keyword argument: '{name}'"
                    )
                arguments[name] = value
            for name, value2 in self.args.items():
                if name not in arguments:
                    if value2 is None:
                        raise RainDuckArgumentError(f"Argument {name} not given.")
                    arguments[name] = value2
            macros = {}
            for name, value in arguments.items():
                macros[name] = Macro(name, OrderedDict(), value)
            code = cast(CodeBlock, code).add_macros(macros)
        return code


class CodeBlock(CodeElement):

    macros: dict[str, Macro]
    my_macros: dict[str, Macro]
    parent: "CodeBlock | None"
    code: list[CodeElement]

    def __init__(
        self,
        tokens: list[Token] = [],
        macro_defs: list[Token] = [],
        parent: "CodeBlock | None" = None,
        file_path: Path | None = None,
    ) -> None:
        self.macros = {}
        self.my_macros = self.macros
        while macro_defs:
            match macro_defs.pop(0):
                case Word(name, line_pos, char_pos):
                    if not macro_defs:
                        raise RainDuckSyntaxError(
                            "Expected macro definition.", line_pos, char_pos
                        )
                    args: OrderedDict[str, CodeElement | None] = OrderedDict()
                    match macro_defs[0]:
                        case Char("(", bracket_line_pos, bracket_char_pos):  # Take args
                            del macro_defs[0]
                            while macro_defs:
                                token = macro_defs.pop(0)
                                match token:
                                    case Char(")"):
                                        break
                                if not macro_defs:
                                    raise RainDuckSyntaxError(
                                        "Macro arguments definition not finished.",
                                        bracket_line_pos,
                                        bracket_char_pos,
                                    )
                                match token:
                                    case Word(arg_name):
                                        match macro_defs.pop(0):
                                            case Char(";" | ")" as c):
                                                args[arg_name] = None
                                                if c == ")":
                                                    break
                                            case Char("=", cp, lp):
                                                if not macro_defs:
                                                    raise RainDuckSyntaxError(
                                                        "Expected default argument value.",
                                                        cp,
                                                        lp,
                                                    )
                                                args[arg_name] = _take_elem(
                                                    macro_defs, self, file_path
                                                )
                                                if not macro_defs:
                                                    raise RainDuckSyntaxError(
                                                        "Macro arguments definition not finished.",
                                                        bracket_line_pos,
                                                        bracket_char_pos,
                                                    )
                                                match macro_defs[0]:
                                                    case Char(";"):
                                                        del macro_defs[0]
                                                    case Char(")"):
                                                        pass
                                                    case t:
                                                        raise RainDuckSyntaxError(
                                                            "';' or ')' expected.",
                                                            t.line_pos,
                                                            t.char_pos,
                                                        )
                    if len(macro_defs) < 2:
                        raise RainDuckSyntaxError(
                            "Expected macro definition.", line_pos, char_pos
                        )
                    match macro_defs.pop(0):
                        case Char("="):
                            block = CodeBlock.take(macro_defs, self, file_path)
                            if block is None:
                                t2: Token = macro_defs[0]
                                raise RainDuckSyntaxError(
                                    "Code block expected.", t2.line_pos, t2.char_pos
                                )
                            self.macros[name] = Macro(name, args, block)
                case Special("import", import_path, lp, cp):
                    if file_path is None:
                        raise RainDuckImportError(
                            "Imports not supported here: no file path.", lp, cp
                        )
                    imported_macros = _import(file_path, import_path)
                    self.macros.update(imported_macros)
        self.parent = parent
        self.code = parse_list(tokens, self, file_path)

    def transpile(self, inverse: bool = False) -> list["BrainFuck"]:
        return sum(
            [elem.transpile(inverse) for elem in self.code[:: -1 if inverse else 1]], []
        )

    @classmethod
    def take(
        cls,
        code: list[Token],
        parent: "CodeBlock | None" = None,
        file_path: Path | None = None,
    ) -> Self | None:
        match code[0]:
            case Char("{", char_pos, line_pos):
                del code[0]
                macro_defs: list[Token] = []
                match code[0]:
                    case Word("let", let_line_pos, let_char_pos):
                        del code[0]
                        brackets = 0
                        while code:
                            match code.pop(0), brackets:
                                case Word("in"), 0:
                                    break
                                case Char("}", end_line_pos, end_char_pos), 0:
                                    e = RainDuckSyntaxError(
                                        "End of group before end of let-in block.",
                                        end_line_pos,
                                        end_char_pos,
                                    )
                                    e.add_pointer(let_line_pos, let_char_pos)
                                    raise e
                                case Char("{") as t, _:
                                    brackets += 1
                                    macro_defs.append(t)
                                case Char("}") as t, _:
                                    brackets -= 1
                                    macro_defs.append(t)
                                case t, _:
                                    macro_defs.append(t)
                        else:
                            raise RainDuckSyntaxError(
                                "End of file before end of let-lin block",
                                let_char_pos,
                                let_line_pos,
                            )
                tokens: list[Token] = []
                brackets = 0
                while code:
                    match code.pop(0), brackets:
                        case Char("}", end_line_pos, end_char_pos), 0:
                            break
                        case Char("{") as t, _:
                            brackets += 1
                            tokens.append(t)
                        case Char("}") as t, _:
                            brackets -= 1
                            tokens.append(t)
                        case t, _:
                            tokens.append(t)
                else:
                    raise RainDuckSyntaxError(
                        "End of file before end of let-lin block", char_pos, line_pos
                    )
                return cls(tokens, macro_defs, parent, file_path)
        return None

    def add_macros(self, macros: dict[str, Macro]) -> Self:
        self.macros = self.my_macros | macros  # TODO: This should not be possible.
        return self


class MacroCall(CodeElement):

    name: str
    args: list[CodeElement]
    kwds: dict[str, CodeElement]
    parent: CodeBlock | None
    line_pos: int | None
    char_pos: int | None

    def __init__(
        self,
        name: str,
        args: list[CodeElement] = [],
        kwds: dict[str, CodeElement] = {},
        parent: CodeBlock | None = None,
        line_pos: int | None = None,
        char_pos: int | None = None,
    ) -> None:
        self.name = name
        self.args = args
        self.kwds = kwds
        self.parent = parent
        self.line_pos = line_pos
        self.char_pos = char_pos

    @classmethod
    def take(
        cls,
        code: list[Token],
        parent: "CodeBlock | None" = None,
        file_path: Path | None = None,
    ) -> "CodeElement | None":
        match code[0]:
            case Word(name, line_pos, char_pos):
                del code[0]
                args = []
                kwds = {}
                if code:
                    match code[0]:
                        case Char("(", bracket_line_pos, bracket_char_pos):  # )
                            del code[0]
                            keywords = False
                            while code:
                                if len(code) < 2:
                                    raise RainDuckSyntaxError(
                                        "Arguments not finished, missing ')'",
                                        bracket_line_pos,
                                        bracket_char_pos,
                                    )
                                match code[0], code[1], keywords:
                                    case Word(argname), Char("=", lp, cp), _:
                                        del code[0]
                                        del code[0]
                                        if not code:
                                            raise RainDuckSyntaxError(
                                                "Expected argument value.", lp, cp
                                            )
                                        kwds[argname] = _take_elem(
                                            code, parent, file_path
                                        )
                                        keywords = True
                                    case _, _, False:
                                        args.append(_take_elem(code, parent, file_path))
                                    case t, _, True:
                                        raise RainDuckArgumentError(
                                            "Positional argument follows keyword argument.",
                                            t.line_pos,
                                            t.char_pos,
                                        )
                                if not code:
                                    raise RainDuckSyntaxError(
                                        "Arguments not finished, missing ')'",
                                        bracket_line_pos,
                                        bracket_char_pos,
                                    )
                                match code.pop(0):
                                    case Char(";"):
                                        pass
                                    case Char(")"):
                                        break
                                    case _:
                                        raise RainDuckSyntaxError(
                                            "Expected ';' or ')'."
                                        )
                return cls(name, args, kwds, parent, line_pos, char_pos)
        return None

    def transpile(self, inverse: bool = False) -> list["BrainFuck"]:
        block = self.parent
        while not (block is None):
            if self.name in block.macros:
                try:
                    return block.macros[self.name](*self.args, **self.kwds).transpile(
                        inverse
                    )
                except RainDuckError as e:
                    e.add_pointer(self.line_pos, self.char_pos, self.name)
                    raise e
            block = block.parent
        raise RainDuckNameError(
            f"'{self.name}' is not defined.", self.line_pos, self.char_pos
        )


def _import(
    file_path: Path,
    import_path: str,
    line_pos: int | None = None,
    char_pos: int | None = None,
) -> dict[str, Macro]:
    path = file_path.parent / import_path
    if not path.is_file():
        raise RainDuckImportError(f"File {import_path} not found.", line_pos, char_pos)
    with path.open() as f:
        imported_code = f.read()
    try:
        from rainduck.transpiler import parse

        imported_macros = parse(imported_code, path).macros
    except RainDuckError as e:
        e.add_pointer(line_pos, char_pos, import_path)
        raise e
    for m in imported_macros.values():
        m.name = import_path + ": " + m.name
    return imported_macros


def _take_elem(
    tokens: list[Token],
    parent: "CodeBlock | None" = None,
    file_path: Path | None = None,
) -> CodeElement:
    for elem_cls in code_elements:
        elem = elem_cls.take(tokens, parent, file_path)
        if not (elem is None):
            return elem
    t = tokens[0]
    raise RainDuckSyntaxError("Unrecognized pattern", t.line_pos, t.char_pos)


def parse_list(
    tokens: list[Token],
    parent: "CodeBlock | None" = None,
    file_path: Path | None = None,
) -> list[CodeElement]:
    result = []
    while tokens:
        result.append(_take_elem(tokens, parent, file_path))
    return result
