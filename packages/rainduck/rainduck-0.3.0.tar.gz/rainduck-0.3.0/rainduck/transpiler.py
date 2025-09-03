from pathlib import Path

from rainduck.code_elements import CodeBlock
from rainduck.errors import RainDuckSyntaxError
from rainduck.tokens import tokenize


def parse(code: str, file_path: Path | None = None) -> CodeBlock:
    tokens = tokenize("{" + code + "}")
    block = CodeBlock.take(tokens, file_path=file_path)
    if tokens:
        t = tokens[0]
        raise RainDuckSyntaxError(line_pos=t.line_pos, char_pos=t.char_pos)
    if block is None:
        raise RainDuckSyntaxError
    return block


def transpile(code: str, file_path: Path | None = None) -> str:
    block = parse(code, file_path)
    bf = block.transpile()
    return "".join(str(x) for x in bf)
