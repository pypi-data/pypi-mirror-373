import pytest

from anbimapy.anbima import Anbima


@pytest.fixture(scope="session")
def anbima():
    return Anbima("", "")
