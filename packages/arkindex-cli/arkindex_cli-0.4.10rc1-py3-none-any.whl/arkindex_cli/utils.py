import datetime
from getpass import getpass
from timeit import default_timer

from rich import print


def ask(prompt: str, default: str = None, hidden: bool = False) -> str:
    """
    Ask for input with an optional default value.
    """
    if default is not None:
        # Add the default to the prompt
        # white is actually gray in a terminal, bright_white is white
        prompt += f" [/]({default})"

    print(f"[bold]{prompt}: ", end="")

    input_function = getpass if hidden else input
    return input_function("") or default


class Timer:
    """
    A context manager to help measure execution times
    """

    def __init__(self):
        self.timer = default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        end = self.timer()
        self.elapsed = end - self.start
        self.delta = datetime.timedelta(seconds=self.elapsed)
