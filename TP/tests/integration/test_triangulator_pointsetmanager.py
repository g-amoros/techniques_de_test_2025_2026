"""Tests d'intégration entre le Triangulator et le PointSetManager (mocké)."""

import struct
import uuid
from unittest.mock import MagicMock, patch

import requests  # Les librairies tierces doivent être séparées


def test_workflow_nominal(client):
    """Test le flux complet : GET /triangulation/<id>.

    On mock la réponse du PointSetManager pour ne pas dépendre du réseau.
    """
    fake_id = str(uuid.uuid4())

    # Préparation d'un binaire PointSet valide (3 points formant un triangle)
    ps_data = struct.pack("<L", 3) + struct.pack("<ffffff", 0, 0, 1, 0, 0, 1)

    # Mock de requests.get
    with patch("src.app.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = ps_data
        mock_get.return_value = mock_response

        # Appel à notre API
        response = client.get(f"/triangulation/{fake_id}")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/octet-stream"


def test_pointset_manager_404(client):
    """Si PSM renvoie 404, on doit renvoyer 404."""
    fake_id = str(uuid.uuid4())
    with patch("src.app.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = client.get(f"/triangulation/{fake_id}")
        assert response.status_code == 404


def test_pointset_manager_500(client):
    """Si PSM renvoie 500, on doit renvoyer 503 (Service Unavailable)."""
    fake_id = str(uuid.uuid4())
    with patch("src.app.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        response = client.get(f"/triangulation/{fake_id}")
        assert response.status_code == 503
        assert response.json["code"] == "SERVICE_UNAVAILABLE"


def test_pointset_manager_unexpected_status(client):
    """Si PSM renvoie un code inattendu (ex: 403), on renvoie 503."""
    fake_id = str(uuid.uuid4())
    with patch("src.app.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 403  # Forbidden par exemple
        mock_get.return_value = mock_response

        response = client.get(f"/triangulation/{fake_id}")
        
        # Cela va déclencher le bloc `if response.status_code != 200`
        assert response.status_code == 503
        assert response.json["code"] == "POINTSET_MANAGER_ERROR"


def test_pointset_manager_connection_error(client):
    """Si la connexion au PSM échoue, on doit renvoyer 503."""
    fake_id = str(uuid.uuid4())
    with patch("src.app.requests.get") as mock_get:
        # Simulation d'une exception réseau
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        response = client.get(f"/triangulation/{fake_id}")
        assert response.status_code == 503
        assert "Échec de communication" in response.json["message"]


def test_pointset_manager_invalid_binary(client):
    """Si PSM renvoie 200 mais un binaire pourri, on doit renvoyer 500."""
    fake_id = str(uuid.uuid4())
    with patch("src.app.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Binaire invalide (trop court)
        mock_response.content = b"\x00\x00"
        mock_get.return_value = mock_response

        response = client.get(f"/triangulation/{fake_id}")
        assert response.status_code == 500
        assert response.json["code"] == "INVALID_POINTSET"


def test_triangulation_failure(client):
    """Si l'algo de triangulation plante, on doit renvoyer 500."""
    fake_id = str(uuid.uuid4())
    ps_data = struct.pack("<L", 3) + struct.pack("<ffffff", 0, 0, 1, 0, 0, 1)

    with patch("src.app.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = ps_data
        mock_get.return_value = mock_response

        # On mock core.triangulate_pointset pour qu'il lève une exception
        with patch("src.app.triangulate_pointset") as mock_algo:
            mock_algo.side_effect = Exception("Oups algo crash")

            response = client.get(f"/triangulation/{fake_id}")
            assert response.status_code == 500
            assert response.json["code"] == "TRIANGULATION_FAILED"


def test_encoding_failure(client):
    """Si l'encodage du résultat plante, on doit renvoyer 500."""
    fake_id = str(uuid.uuid4())
    ps_data = struct.pack("<L", 3) + struct.pack("<ffffff", 0, 0, 1, 0, 0, 1)

    with patch("src.app.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = ps_data
        mock_get.return_value = mock_response

        # On mock binary_utils.triangles_to_binary pour qu'il lève une exception
        with patch("src.app.triangles_to_binary") as mock_encode:
            mock_encode.side_effect = Exception("Oups encoding crash")

            response = client.get(f"/triangulation/{fake_id}")
            assert response.status_code == 500
            assert response.json["code"] == "ENCODING_FAILED"