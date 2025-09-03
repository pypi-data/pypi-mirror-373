import sys
from pathlib import Path

import typer
from rich.console import Console

from rainduck.errors import RainDuckError
from rainduck.transpiler import transpile

app = typer.Typer()
err_console = Console(stderr=True)


@app.command()
def main(source: str, output: str | None = None) -> None:
    source_path = Path(source)
    with source_path.open() as f:
        rainduck = f.read()
    try:
        brainfuck = transpile(rainduck, source_path)
    except RainDuckError as e:
        err_console.print(e.colored())
        sys.exit(1)
    if output is None:
        if source.endswith(".rd"):
            out_filename = source[:-2] + "bf"
        else:
            out_filename = source + ".bf"
    else:
        out_filename = output
    with open(out_filename, "w") as f:
        f.write(brainfuck)


if __name__ == "__main__":
    app()
