# Modified from typeshed
import sys
from _typeshed import ReadableBuffer, SupportsTrunc
from collections.abc import Callable
from typing import SupportsFloat, SupportsInt, TypeVar
from typing_extensions import SupportsIndex, TypeAlias

from Xlib.error import XError
from Xlib.protocol.rq import Request

_T = TypeVar("_T")
ErrorHandler: TypeAlias = Callable[[XError, Request | None], _T]

# mypy 1.7 added these to `_typeshed`, and checks for Python 3.7+.
# Older targets need mypy 1.5 or older, so they get a copy.
if sys.version_info >= (3, 7):
    from _typeshed import ConvertibleToFloat as ConvertibleToFloat, ConvertibleToInt as ConvertibleToInt
else:
    # Anything that can be passed to the int/float constructors
    ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex | SupportsTrunc
    ConvertibleToFloat: TypeAlias = str | ReadableBuffer | SupportsFloat | SupportsIndex
