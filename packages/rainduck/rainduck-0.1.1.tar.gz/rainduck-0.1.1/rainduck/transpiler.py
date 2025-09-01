from rainduck.code_elements import CodeBlock, parse_list
from rainduck.errors import RainDuckSyntaxError
from rainduck.tokens import tokenize


def transpile(code: str) -> str:
    tokens = tokenize("{" + code + "}")
    block = CodeBlock.take(tokens)
    if tokens:
        t = tokens[0]
        raise RainDuckSyntaxError(line_pos=t.line_pos, char_pos=t.char_pos)
    if block is None:
        raise RainDuckSyntaxError
    bf = block.transpile()
    return "".join(str(x) for x in bf)
