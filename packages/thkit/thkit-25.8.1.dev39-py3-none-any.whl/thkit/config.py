import json
from pathlib import Path
from warnings import warn

import yaml
from cerberus import Validator


### ANCHOR: YAML config
def validate_config(
    config_dict=None,
    config_file=None,
    schema_dict=None,
    schema_file=None,
    allow_unknown=False,
    require_all=False,
):
    """Validate the config file with the schema file.

    Args:
        config_dict (dict, optional): config dictionary. Defaults to None.
        config_file (str, optional): path to the YAML config file, will override `config_dict`. Defaults to None.
        schema_dict (dict, optional): schema dictionary. Defaults to None.
        schema_file (str, optional): path to the YAML schema file, will override `schema_dict`. Defaults to None.
        allow_unknown (bool, optional): whether to allow unknown fields in the config file. Defaults to False.
        require_all (bool, optional): whether to require all fields in the schema file to be present in the config file. Defaults to False.

    Raises:
        ValueError: if the config file does not match the schema
    """
    if not config_dict and config_file:
        config_dict = yaml.safe_load(open(config_file))
    if not schema_dict and schema_file:
        schema_dict = yaml.safe_load(open(schema_file))

    if not config_dict:
        raise ValueError("Must provide either `config_dict` or `config_file`")
    if not schema_dict:
        raise ValueError("Must provide either `schema_dict` or `schema_file`")

    ## validate
    v = Validator(allow_unknown=allow_unknown, require_all=require_all)
    v.schema = schema_dict  # set the schema separately to ensure it is valid
    is_valid = v.validate(config_dict)
    if not is_valid:
        config_path = Path(config_file).as_posix() if config_file else "<input dict>"
        schema_path = Path(schema_file).as_posix() if schema_file else "<input dict>"
        raise ValueError(
            f"Found incorrect configurations\n"
            f"Config: {config_path}\n"
            f"Schema: {schema_path}\n"
            f"Error:\n{v.errors}\n"
        )
    return


def load_config(filename: str | Path) -> dict:
    """Load data from a JSON or YAML file. The YAML file can contain variable-interpolation, will be processed by [OmegaConf](https://omegaconf.readthedocs.io/en/2.2_branch/usage.html#variable-interpolation).

    Args:
    filename (Union[str, Path]): The filename to load data from, whose suffix should be .json, jsonc, .yml, or .yml

    Returns:
        jdata: (dict) The data loaded from the file
    """
    if Path(filename).suffix in [".json", ".jsonc"]:
        jdata = load_jsonc(filename)
    elif Path(filename).suffix in [".yml", ".yml"]:
        from omegaconf import OmegaConf

        conf = OmegaConf.load(filename)
        jdata = OmegaConf.to_container(conf, resolve=True)
    else:
        raise ValueError(f"Unsupported file format: {filename}")

    if not jdata:
        jdata = {}
        warn(f"Empty config file: {filename}")
    return jdata


def load_jsonc(filename: str) -> dict:
    """Load data from a JSON file that allow comments."""
    with open(filename) as f:
        lines = f.readlines()
    cleaned_lines = [line.strip().split("//", 1)[0] for line in lines if line.strip()]
    text = "\n".join(cleaned_lines)
    jdata = json.loads(text)
    return jdata
