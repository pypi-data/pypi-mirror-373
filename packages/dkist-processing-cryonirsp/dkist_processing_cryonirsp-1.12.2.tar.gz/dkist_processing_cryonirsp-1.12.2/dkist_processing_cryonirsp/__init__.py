"""Init."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from dkist_service_configuration.logging import logger  # first import to set logging.BasicConfig

try:
    __version__ = version(distribution_name=__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
