import importlib
import logging
import subprocess
import sys
from pathlib import Path

from thkit.stuff import text_fill_center


######ANCHOR: logger
def strip_ansi_codes(msg: str) -> str:
    """Strip ANSI codes for color formatting from a string."""
    for n in [0, 91, 92, 93, 94, 95, 96, 97, 98, 99]:
        code = f"\033[{n}m"
        msg = msg.replace(code, "")
    return msg


def create_logger(
    logger_name: str = None,
    log_file: str = None,
    level: str = "INFO",
    level_logfile: str = None,
) -> logging.Logger:
    """Create and configure a logger with console and optional file handlers."""
    # "debug": "%(asctime)s | %(levelname)s: %(message)s | %(funcName)s:%(lineno)d",

    logger = logging.getLogger(logger_name or __name__)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    ## Prevent duplicate handlers
    if not logger.hasHandlers():
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, level.upper(), logging.INFO))
        ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%b%d %H:%M"))
        logger.addHandler(ch)

        # File handler
        if log_file:
            fh = logging.FileHandler(log_file, mode="a")
            fh.setLevel(getattr(logging, (level_logfile or level).upper(), logging.INFO))
            fh.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s: %(message)s", "%Y%b%d %H:%M:%S")
            )

            # wrap emit to strip ANSI codes before writing
            old_emit = fh.emit

            def new_emit(record):
                record.msg = strip_ansi_codes(str(record.msg))
                old_emit(record)

            fh.emit = new_emit

            logger.addHandler(fh)
    return logger


def check_package(
    package_name: str,
    auto_install: bool = False,
    git_repo: str = None,
    conda_channel: str = None,
):
    """Check if the required packages are installed"""
    try:
        importlib.import_module(package_name)
    except ImportError:
        if auto_install:
            install_package(package_name, git_repo, conda_channel)
        else:
            raise ImportError(
                f"Required package `{package_name}` is not installed. Please install it.",
            )
    return


def install_package(
    package_name: str,
    git_repo: str | None = None,
    conda_channel: str | None = None,
) -> None:
    """Install the required package:
        - Default using: `pip install -U {package_name}`
        - If `git_repo` is provided: `pip install -U git+{git_repo}`
        - If `conda_channel` is provided: `conda install -c {conda_channel} {package_name}`

    Args:
        package_name (str): package name
        git_repo (str): git path for the package. Default: None. E.g., http://somthing.git
        conda_channel (str): conda channel for the package. Default: None. E.g., conda-forge
    """
    if git_repo:
        cmd = ["pip", "install", "-U", f"git+{git_repo}"]
    elif conda_channel:
        cmd = ["conda", "install", "-c", conda_channel, package_name, "-y"]
    else:
        cmd = ["pip", "install", "-U", package_name]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install `{package_name}`: {e}")
    return


def get_func_args(func):
    """Get the arguments of a function"""
    import inspect

    argspec = inspect.getfullargspec(func)
    no_default_args = ["no_default_value"] * (len(argspec.args) - len(argspec.defaults))
    all_values = no_default_args + list(argspec.defaults)
    argsdict = dict(zip(argspec.args, all_values))
    return argsdict


def dependency_info(modules=["numpy", "polars", "thkit", "ase"]) -> str:
    """Get the dependency information

    Note:
        Use `importlib` instead of `__import__` for clarity.
    """
    lines = [text_fill_center(" Dependencies ", fill="-", length=70)]
    for pkg in modules:
        try:
            mm = importlib.import_module(pkg)
            ver = getattr(mm, "__version__", "unknown").split("+")[0]
            path = getattr(mm, "__path__", ["unknown path"])[0]
            lines.append(f"{pkg:>12}  {ver:<12} {Path(path).as_posix()}")
        except ImportError:
            lines.append(f"{pkg:>12}  {'unknown':<12} ")
        except Exception:
            lines.append(f"{pkg:>12}  {'':<12} unknown version or path")
    ### Python version
    lines.append(
        f"{'python':>12}  {sys.version.split(' ')[0]:<12} {Path(sys.executable).as_posix()}"
    )
    return "\n".join(lines) + "\n"
