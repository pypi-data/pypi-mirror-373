import base64
import random
import string
import time
from typing import Generator
from warnings import warn


def chunk_list(input_list: list, n: int) -> Generator:
    """Yield successive n-sized chunks from `input_list`."""
    for i in range(0, len(input_list), n):
        yield input_list[i : i + n]


### ANCHOR: index tools
def unpack_idx(list_inputs: list[int | str]) -> list[int]:
    """Expand mixed index tokens into a list of integers.
    Accepts ints or strings in 'start-end[:step]' (inclusive).

    Examples: [1, 2, "3-5:2", "6-10"] -> [1, 2, 3, 5, 6, 7, 8, 9, 10]
    """
    idx = []
    for item in list_inputs:
        if isinstance(item, int):
            idx.append(item)
        elif isinstance(item, str):
            parts = item.split(":")
            step = int(parts[1]) if len(parts) > 1 else 1
            start, end = map(int, parts[0].split("-"))
            idx.extend(range(start, end + 1, step))
    return idx


### ANCHOR: string modifier
def text_fill_center(input_text="example", fill="-", length=60):
    """Create a line with centered text."""
    text = f"{input_text}"
    return text.center(length, fill)


def text_fill_left(input_text="example", margin=15, fill_left="-", fill_right=" ", length=60):
    """Create a line with left-aligned text."""
    text = f"{(fill_left * margin)}{input_text}"
    return text.ljust(length, fill_right)


def text_fill_box(input_text="", fill=" ", sp="|", length=60):
    """Put the string at the center of |  |."""
    strs = input_text.center(length, fill)
    box_text = sp + strs[1 : len(strs) - 1 :] + sp
    return box_text


def text_repeat(input_str: str, length: int) -> str:
    """Repeat the input string to a specified length."""
    text = (input_str * ((length // len(input_str)) + 1))[:length]
    return text


def text_color(text: str, color: str = "blue") -> str:
    """ANSI escape codes for color the text.
    follow [this link](https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences) for more details.
    """
    ### Make color text with \033[<code>m
    ansi_code = {
        "red": "91",
        "green": "92",
        "yellow": "93",
        "blue": "94",
        "magenta": "95",
        "cyan": "96",
        "white": "97",
    }
    if color not in ansi_code:
        warn(f"Color '{color}' is not supported. Choose from {list(ansi_code.keys())}.")
        color = "white"

    text = "\033[" + ansi_code[color] + "m" + text + "\033[0m"
    return text


def time_uuid() -> str:
    timestamp = int(time.time() * 1.0e6)
    rand = random.getrandbits(10)
    unique_value = (timestamp << 10) | rand  # Combine timestamp + random bits
    text = base64.urlsafe_b64encode(unique_value.to_bytes(8, "big")).decode().rstrip("=")
    return text.replace("-", "_")


def simple_uuid():
    """Generate a simple random UUID of 4 digits."""
    rnd_letter = random.choice(string.ascii_uppercase)  # ascii_letters
    rnd_num = random.randint(100, 999)
    return f"{rnd_letter}{rnd_num}"
