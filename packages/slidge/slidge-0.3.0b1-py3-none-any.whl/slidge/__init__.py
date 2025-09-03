"""
The main slidge package.

Contains importable classes for a minimal function :term:`Legacy Module`.
"""

import sys
import warnings
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from . import slixfix  # noqa: F401
from .command import FormField, SearchResult  # noqa: F401
from .contact import LegacyContact, LegacyRoster  # noqa: F401
from .core import config as global_config  # noqa: F401
from .core.gateway import BaseGateway  # noqa: F401
from .core.session import BaseSession  # noqa: F401
from .db import GatewayUser  # noqa: F401
from .group import LegacyBookmarks, LegacyMUC, LegacyParticipant  # noqa: F401
from .main import main as main_func
from .util.types import MucType  # noqa: F401
from .util.util import addLoggingLevel


def entrypoint(module_name: str) -> None:
    """
    Entrypoint to be used in ``__main__.py`` of
    :term:`legacy modules <Legacy Module>`.

    :param module_name: An importable :term:`Legacy Module`.
    """
    main_func(module_name)


def formatwarning(
    message: Any, category: Any, filename: Any, lineno: Any, line: str = ""
) -> str:
    return f"{filename}:{lineno}:{category.__name__}:{message}\n"


warnings.formatwarning = formatwarning  # type:ignore

try:
    __version__ = version("slidge")
except PackageNotFoundError:
    # package is not installed
    __version__ = "dev"


__all__ = [
    "__version__",
    "BaseGateway",
    "BaseSession",
    # For backwards compatibility, these names are still importable from the
    # top-level slidge module, but this is deprecated.
    # "GatewayUser",
    # "LegacyBookmarks",
    # "LegacyMUC",
    # "LegacyContact",
    # "LegacyParticipant",
    # "LegacyRoster",
    # "MucType",
    # "FormField",
    # "SearchResult",
    "entrypoint",
    "global_config",
]

addLoggingLevel()
