"""
A simple and flexible asset management application built upon the Django framework.

Can also be used as a building block library for more complex applications.
"""
__prog__ = 'amabase'

__version__: str
__version_tuple__: tuple
try:
    from amabase._version import __version__, __version_tuple__  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    __version__ = '?'
    __version_tuple__ = (0, 0, 0, '?')

from amabase.conf import main

__all__ = ('main', '__prog__', '__version__', '__version_tuple__')
