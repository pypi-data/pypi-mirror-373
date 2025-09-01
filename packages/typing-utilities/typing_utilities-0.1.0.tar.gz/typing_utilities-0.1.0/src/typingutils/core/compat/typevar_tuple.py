# pyright: basic
import sys
from typing import Any

if sys.version_info >= (3, 11):

    from typing import TypeVarTuple # pyright: ignore[reportAssignmentType, reportAttributeAccessIssue]

else:

    from typing_extensions import TypeVarTuple # pyright: ignore[reportMissingModuleSource] # pragma: no cover

