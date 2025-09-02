import re
import rich
import arrow
import pathlib
from pathlib import Path
import urllib.parse

from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.pretty import pprint, Pretty

console = Console()

def seed_everything(seed=42):
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    # import torch if it is available
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pprint("torch not imported, skipping torch seed_everything")
        pass


def now_str(sep_date_time="."):
    assert sep_date_time in [
        ".",
        "_",
        "-",
    ], "sep_date_time must be one of '.', '_', or '-'"
    now_string = arrow.now().format(f"YYYYMMDD{sep_date_time}HHmmss")
    return now_string


def norm_str(in_str):
    # Replace one or more whitespace characters with a single underscore
    norm_string = re.sub(r"\s+", "_", in_str)
    # Remove leading and trailing spaces
    norm_string = norm_string.strip()
    return norm_string


def pprint_box(obj, title="", border_style="green"):
    """
    Pretty print an object in a box.
    """
    rich.print(
        Panel(Pretty(obj, expand_all=True), title=title, border_style=border_style)
    )

def console_rule(msg, do_norm_msg=True, is_end_tag=False):
    msg = norm_str(msg) if do_norm_msg else msg
    if is_end_tag:
        console.rule(f"</{msg}>")
    else:
        console.rule(f"<{msg}>")


def console_log(func):
    def wrapper(*args, **kwargs):
        console_rule(func.__name__)
        result = func(*args, **kwargs)
        console_rule(func.__name__, is_end_tag=True)
        return result

    return wrapper


class ConsoleLog:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        console_rule(self.message)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        console_rule(self.message, is_end_tag=True)
        if exc_type is not None:
            print(f"An exception of type {exc_type} occurred.")
            print(f"Exception message: {exc_value}")


def pprint_local_path(local_path, tag=""):
    # Create a file URI
    file_path = Path(local_path).resolve()
    is_file = file_path.is_file()
    is_dir = file_path.is_dir()
    type_str = "📄" if is_file else "📁" if is_dir else "❓"
    file_uri = file_path.as_uri()
    content_str = f"{type_str} [link={file_uri}]{file_uri}[/link]"
    if isinstance(tag, str) and len(tag) > 0:
        with ConsoleLog(tag):
            console.print(content_str)
    else:
        # If tag is not provided, just print the link
        console.print(f"{content_str}")
    return file_uri
