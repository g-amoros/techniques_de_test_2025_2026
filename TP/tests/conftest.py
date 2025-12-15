"""Configuration et fixtures Pytest globales."""

import pytest

from src.app import app


@pytest.fixture
def client():
    """Crée un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client