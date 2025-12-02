from flask import Flask, request, jsonify, Response
from src.core import triangulate_pointset
from src.binary_utils import pointset_from_binary, triangles_to_binary
import requests
import os

app = Flask(__name__)

# URL du PointSetManager (mockable via env var)
PSM_URL = os.environ.get("POINT_SET_MANAGER_URL", "http://localhost:8000")

@app.route('/triangulation/<point_set_id>', methods=['GET'])
def get_triangulation(point_set_id):
    """
    Route principale :
    1. Récupère le PointSet binaire depuis le PointSetManager.
    2. Convertit le binaire en liste de points.
    3. Calcule la triangulation.
    4. Convertit le résultat en binaire.
    5. Renvoie la réponse.
    """
    # TODO: Implémenter la logique complète
    # Pour l'instant, on renvoie une 501 Not Implemented pour faire échouer les tests d'intégration
    return jsonify({"error": "Not implemented yet"}), 501

if __name__ == '__main__':
    app.run(debug=True)