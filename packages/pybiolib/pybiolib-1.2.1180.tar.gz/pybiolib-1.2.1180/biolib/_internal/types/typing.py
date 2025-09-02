import sys

# import and expose everything from the typing module
from typing import *  # noqa:F403 pylint: disable=wildcard-import, unused-wildcard-import

if sys.version_info < (3, 8):  # noqa: UP036
    from typing_extensions import Literal, TypedDict  # pylint: disable=unused-import

if sys.version_info < (3, 11):  # noqa: UP036
    from typing_extensions import NotRequired  # pylint: disable=unused-import
