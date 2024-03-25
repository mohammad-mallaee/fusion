import typer

from shift import __app_name__, __version__
from shift.index import shift
from shift.sync import sync

app = typer.Typer()


@app.command()
def main(args: list[str]):
    match args[0]:
        case 'sync':
            sync(*args)
            return
        case 'test':
            print('testing is not supported yet')
            return
        case _:
            shift(*args)
            return
