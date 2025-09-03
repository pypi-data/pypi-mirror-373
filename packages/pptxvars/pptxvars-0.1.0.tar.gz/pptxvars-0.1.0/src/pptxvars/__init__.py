from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pptxvars")
except PackageNotFoundError:  # local dev, not installed
    __version__ = "0.0.0"

from .replacer import apply_vars, load_vars, format_outpath  # re-export

__all__ = ["__version__", "apply_vars", "load_vars", "format_outpath"]
