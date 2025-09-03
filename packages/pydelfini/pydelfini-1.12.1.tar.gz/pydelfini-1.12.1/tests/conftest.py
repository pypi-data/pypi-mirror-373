import pytest
from pydelfini.delfini_core import AuthenticatedClient


@pytest.fixture
def client():
    return AuthenticatedClient(
        base_url="https://delfini.test/api/v1", token="test-token"
    )
