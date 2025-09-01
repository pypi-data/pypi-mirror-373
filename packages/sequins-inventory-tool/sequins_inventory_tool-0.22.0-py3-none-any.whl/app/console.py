from rich.console import Console

console = Console()


def get_console():
    """Obtain a console instance, provided so we can patch it in tests."""
    return console
