import pytest
from django.test import Client


@pytest.fixture(scope="session")
def app():
    return Client()

