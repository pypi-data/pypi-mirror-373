from dataclasses import dataclass


@dataclass
class PointerToCode:
    """Points some location in RainDuck code (where error occured)"""

    line_pos: int | None = None
    char_pos: int | None = None
    macro_name: str | None = None

    def __str__(self) -> str:
        result = ""
        if not (self.line_pos is None):
            result += f"on line {self.line_pos}"
            if not (self.char_pos is None):
                result += f", character {self.char_pos}"
            if not (self.macro_name is None):
                result += ", "
        if not (self.macro_name is None):
            result += f"in '{self.macro_name}'"
        return result


class RainDuckError(Exception):
    """Exception raised when error in RainDuck code found"""

    default_message: str = "An error occured."

    message: str
    traceback: list[PointerToCode]

    def __init__(
        self,
        message: str | None = None,
        line_pos: int | None = None,
        char_pos: int | None = None,
        macro_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message if not (message is None) else self.default_message
        if not (line_pos is None and char_pos is None and macro_name is None):
            self.traceback = [PointerToCode(line_pos, char_pos, macro_name)]
        else:
            self.traceback = []

    def to_string(self, color: bool = False) -> str:
        result = (
            (f"[bold red]{self.name}[/bold red]" if color else self.name)
            + ": "
            + self.message
        )
        if self.traceback:
            result += "\n" + "\n".join([str(t) for t in self.traceback[::-1]])
        return result

    @property
    def name(self) -> str:
        cls_name = type(self).__name__
        return cls_name[8:] if cls_name.startswith("RainDuck") else cls_name

    def add_pointer(
        self,
        line_pos: int | None = None,
        char_pos: int | None = None,
        macro_name: str | None = None,
    ) -> None:
        """Add new PointerToCode to traceback"""
        self.traceback.append(PointerToCode(line_pos, char_pos, macro_name))

    def edit_pointer(
        self,
        line_pos: int | None = None,
        char_pos: int | None = None,
        macro_name: str | None = None,
    ) -> None:
        """Edit attributes of the last PointerToCode in traceback."""
        pointer = self.traceback[-1]
        if not (line_pos is None):
            pointer.line_pos = line_pos
        if not (char_pos is None):
            pointer.char_pos = char_pos
        if not (macro_name is None):
            pointer.macro_name = macro_name

    def colored(self) -> str:
        return self.to_string(color=True)

    def __str__(self) -> str:
        return self.to_string(color=False)


class RainDuckTokenError(RainDuckError):
    """Exception raised when error with tokenization of RainDuck code found."""

    default_message = "An error with tokenization occured."


class RainDuckNameError(RainDuckError):
    """Exception raised when called non-existent macro"""

    default_message = "Not defined"
    macro_name: str | None


class RainDuckValueError(RainDuckError):
    """Exception raised when some value in RainDuck code is invalid"""

    default_message = "Invalid value"


class RainDuckArgumentError(RainDuckValueError):
    """Exception raised when macro has invalid arguments."""

    default_message = "Invalid arguments"


class RainDuckSyntaxError(RainDuckError):
    """Exception raised while parsing when invalid syntax foud"""

    default_message = "Invalid syntax"


class RainDuckInversionError(RainDuckError):
    """Exception raised when code can't be inverter by negative nuber"""

    default_message = "Code can't be inverted"


class RainDuckImportError(RainDuckError):
    """Exception raised when fila can't be imported."""
