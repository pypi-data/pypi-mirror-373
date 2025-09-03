"""Top-level package for termai.

Exposes ``__version__`` sourced from installed distribution metadata using
Python 3.12+'s built-in importlib.metadata.
"""

from importlib.metadata import version, PackageNotFoundError

# Distribution name defined in pyproject.toml
_DISTRIBUTION = "termaitrik"

try:
	__version__ = version(_DISTRIBUTION)
except PackageNotFoundError:
	# In non-installed contexts (e.g., running from a raw checkout), fall back
	# to a placeholder. Editable installs will provide metadata.
	__version__ = "0.0.0"

__all__ = ["__version__"]
