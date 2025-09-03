from importlib.metadata import version, PackageNotFoundError

from .core import find_consensus, ccHBGF
from .config import config

# Package Versioning
# ------------------------------------------------------------------------------

try:
    __version__ = version("scutils")
except PackageNotFoundError:  # e.g. when running from source without install
    __version__ = "0.0.0"

# Set package-wide configuraiton variables
# ------------------------------------------------------------------------------

config.LOG_LEVEL = 1 # Warnings Only by default

# Overwrite default config values by $SCUTILS_* os environment variables
config.update_from_environ(prefix='CCHBGF')

# Set up packcage * namespace
# ------------------------------------------------------------------------------

__all__ = [
    'find_consensus',
    'ccHBGF' # an alias for backwards compatibility for 0.1.0
    ]