"""Standard pytest configuration."""
from typing import List, Any

import pytest  # type: ignore
import dictdiffer  # type: ignore
import os
import pprint

pp = pprint.PrettyPrinter(indent=2)


def pytest_assertrepr_compare(op: str, left: Any, right: Any) -> List[str]:  # noqa: U100
    """Pytest comparison function to show dict diffs."""
    output = ["Compare Result:"]

    for line in list(dictdiffer.diff(left, right)):
        output.extend(pp.pformat(line).split("\n"))

    return output


@pytest.fixture()
def repo_root() -> str:
    """Return the real path to the root of the git repo."""
    path = os.path.realpath(os.curdir)

    while True:
        if os.path.exists(os.path.join(path, "setup.py")):
            return path
        path = os.path.realpath(os.path.join(path, ".."))
