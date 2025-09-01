"""SpeeDBeeSynapse custom component development environment tool."""
from __future__ import annotations

import sys
from typing import Any


def print_info(*args: Any) -> None:  # noqa: ANN401
    """Output information message to standard output."""
    print(*args)  # noqa: T201


def print_error(*args: Any) -> None:  # noqa: ANN401
    """Output error message to standard error."""
    print(*args, file=sys.stderr)  # noqa: T201
