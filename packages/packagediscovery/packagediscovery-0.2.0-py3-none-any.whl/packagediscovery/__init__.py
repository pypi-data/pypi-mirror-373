"""Top-level package for Package Discovery."""

from packagediscovery.packages import *  # noqa: F403
from packagediscovery.setuptools import *  # noqa: F403

__author__ = """Yukihiko Shinoda"""
__email__ = "yuk.hik.future@gmail.com"
__version__ = "0.2.0"

__all__ = []
__all__ += packages.__all__  # type:ignore[name-defined] # noqa: F405 pylint: disable=undefined-variable
__all__ += setuptools.__all__  # type:ignore[name-defined] # noqa: F405 pylint: disable=undefined-variable
