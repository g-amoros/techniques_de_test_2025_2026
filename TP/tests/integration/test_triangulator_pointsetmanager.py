import struct
import uuid
from unittest.mock import MagicMock, patch


def test_workflow_nominal(client):
    """
    Test le flux complet : GET /triangulation/<id>
    On mock la réponse du PointSetManager pour ne pas dépendre du réseau.
    """
    fake_id = str(uuid.uuid4())

    # Préparation d'un binaire PointSet valide (3 points formant un triangle)
    ps_data = struct.pack('<L', 3) + struct.pack('<ffffff', 0,0, 1,0, 0,1)

    # Mock de requests.get
    with patch('src.app.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = ps_data
        mock_get.return_value = mock_response

        # Appel à notre API
        response = client.get(f'/triangulation/{fake_id}')

        # Ce test échouera car app.py retourne 501 pour l'instant
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/octet-stream'
        # On devrait vérifier que le body est un binaire Triangles valide

def test_pointset_manager_404(client):
    """Si PSM renvoie 404, on doit renvoyer 404"""
    fake_id = str(uuid.uuid4())
    with patch('src.app.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = client.get(f'/triangulation/{fake_id}')
        assert response.status_code == 404
