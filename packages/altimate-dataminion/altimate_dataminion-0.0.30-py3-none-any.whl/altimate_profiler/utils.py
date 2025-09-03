import hashlib
from typing import Text


def sha256_encoding(string):
    sha256 = hashlib.sha256()
    sha256.update(string.encode("utf-8"))
    return sha256.hexdigest()


# Print utils
def green_bold_string(s: Text) -> Text:
    return f"[bold green]{s}[/bold green]"


def yellow(s: Text) -> Text:
    return f"[yellow]{s}[/yellow]"


def red(s: Text) -> Text:
    return f"[red]{s}[/red]"
