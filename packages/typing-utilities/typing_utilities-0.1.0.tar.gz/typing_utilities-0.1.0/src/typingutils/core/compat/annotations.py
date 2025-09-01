# pyright: basic
# ruff: noqa
import sys

if sys.version_info >= (3, 13):

    from typing import ReadOnly # pyright: ignore[reportAssignmentType, reportAttributeAccessIssue]

else:

    from typing_extensions import ReadOnly # pyright: ignore[reportMissingModuleSource] # pragma: no cover


if sys.version_info >= (3, 11):

    from typing import LiteralString, NotRequired, Required, Unpack # pyright: ignore[reportAssignmentType, reportAttributeAccessIssue]

else:

    from typing_extensions import LiteralString, NotRequired, Required, Unpack # pyright: ignore[reportMissingModuleSource] # pragma: no cover
