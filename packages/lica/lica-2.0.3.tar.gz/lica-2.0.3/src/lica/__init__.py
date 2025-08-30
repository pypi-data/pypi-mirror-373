from ._version import __version__ as __version__


try:
    from enum import StrEnum as StrEnum
# Python 3.9 doesn't incorporate StrEnum
except ImportError:
    from strenum import StrEnum as StrEnum
