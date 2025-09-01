from pathlib import Path

import yaml


#####ANCHOR Read/write files
def write_yaml(jdata: dict, filename: str | Path):
    """Write data to a YAML file."""
    with open(filename, "w") as f:
        yaml.safe_dump(jdata, f, default_flow_style=False, sort_keys=False)
    return


def read_yaml(filename: str | Path) -> dict:
    """Read data from a YAML file."""
    with open(filename) as f:
        jdata = yaml.safe_load(f)
    return jdata


#####ANCHOR Modify data
def combine_text_files(files: list[str], output_file: str, chunk_size: int = 1024):
    """
    Combine text files into a single file in a memory-efficient. Read and write in chunks to avoid loading large files into memory

    Args:
        files (list[str]): List of file paths to combine.
        output_file (str): Path to the output file.
        chunk_size (int, optional): Size of each chunk in KB to read/write. Defaults to 1024 KB.
    """
    chunk_size_byte = chunk_size * 1024
    ### Create parent folder if not exist
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    ### Open the output file for writing and append each file's content incrementally
    with open(output_file, "w") as outfile:
        for file in files:
            with open(file, "r") as infile:
                while chunk := infile.read(chunk_size_byte):  # Read in chunks
                    outfile.write(chunk)
    return


def unpack_dict(nested_dict: dict) -> dict:
    """Unpack one level of nested dictionary."""
    # flat_dict = {
    #     key2: val2 for key1, val1 in nested_dict.items() for key2, val2 in val1.items()
    # }

    ### Use for loop to handle duplicate keys
    flat_dict = {}
    for key1, val1 in nested_dict.items():
        for key2, val2 in val1.items():
            if key2 not in flat_dict:
                flat_dict[key2] = val2
            else:
                raise ValueError(
                    f"Key `{key2}` is used multiple times in the same level of the nested dictionary. Please fix it before unpacking dict."
                )
    return flat_dict


class DotDict(dict):
    ### idea from: https://stackoverflow.com/questions/13520421/recursive-dotdict
    ### Revise by ChatGPT to handle nested lists/tuples/sets
    """
    Dictionary supporting dot notation (attribute access) as well as standard dictionary access.
    Nested dicts and sequences (list/tuple/set) are converted recursively.

    Args:
        dct (dict, optional): Initial dictionary to populate the DotDict. Defaults to empty dict.

    Usage:
        d = DotDict({'a': 1, 'b': {'c': 2, 'd': [3, {'e': 4}]}})
        print(d.b.c)       # 2
        print(d['b']['c']) # 2
        d.b.d[1].e = 42
        print(d.b.d[1].e)  # 42
        print(d.to_dict()) # plain dict
    """

    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__

    def __setitem__(self, key, value):
        """Set item using dot notation or standard dict syntax."""
        super().__setitem__(key, self._wrap(value))

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __init__(self, dct=None):
        if dct is None:
            dct = {}
        for key, value in dct.items():
            self[key] = self._wrap(value)

    def _wrap(self, value):
        if isinstance(value, dict):
            return DotDict(value)
        elif isinstance(value, (list, tuple, set)):
            t = type(value)
            return t(self._wrap(v) for v in value)
        return value

    def to_dict(self):
        """Recursively convert DotDict back to plain dict."""
        result = {}
        for key, value in self.items():
            if isinstance(value, DotDict):
                result[key] = value.to_dict()
            elif isinstance(value, (list, tuple, set)):
                t = type(value)
                result[key] = t(v.to_dict() if isinstance(v, DotDict) else v for v in value)
            else:
                result[key] = value
        return result


#####ANCHOR Download files
def download_rawtext(url: str, outfile: str = None) -> str:
    """Download raw text from a URL."""
    import requests

    res = requests.get(url)
    text = res.text
    if outfile is not None:
        with open(outfile, "w") as f:
            f.write(text)
    return text


#####ANCHOR Convert somthing to something
def txt2str(file_path: str | Path) -> str:
    """Convert a text file to a string"""
    with open(file_path, "r") as f:
        text = f.read()
    return text


def str2txt(text: str, file_path: str | Path) -> None:
    """Convert a string to a text file"""
    with open(file_path, "w") as f:
        f.write(text)
    return


def txt2list(file_path: str | Path) -> list[str]:
    """Convert a text file to a list of lines (without newline characters)"""
    with open(file_path, "r") as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    return lines


def list2txt(lines: list[str], file_path: str | Path) -> None:
    """Convert a list of lines to a text file"""
    lines = [str(line) for line in lines]
    text = "\n".join(lines)
    str2txt(text, file_path)
    return


def float2str(number: float, decimals=6):
    """convert float number to str
    REF: https://stackoverflow.com/questions/2440692/formatting-floats-without-trailing-zeros

    Args:
        number (float): float number
        fmt (str): format of the output string

    Returns:
        s (str): string of the float number
    """
    s = f"{number:.{decimals}f}".rstrip("0").rstrip(".")
    if s == "-0":
        s = "0"
    return s
