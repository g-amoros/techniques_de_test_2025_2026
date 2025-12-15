"""Tests des routes API (erreurs clients, méthodes non autorisées)."""


def test_invalid_uuid(client):
    """Teste que l'API renvoie 400 si l'ID n'est pas un UUID valide."""
    # Test sans mock, juste validation format ID
    response = client.get("/triangulation/ceci-nest-pas-un-uuid")
    # Selon ton plan, on attend 400
    assert response.status_code == 400


def test_method_not_allowed(client):
    """Teste que l'API renvoie 405 si la méthode HTTP est incorrecte."""
    response = client.post("/triangulation/1234")
    assert response.status_code == 405