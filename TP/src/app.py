"""Application Flask pour le microservice Triangulator."""

import os
import uuid

import requests
from flask import Flask, Response, jsonify

from src.binary_utils import pointset_from_binary, triangles_to_binary
from src.core import triangulate_pointset

app = Flask(__name__)

# URL du PointSetManager (modifiable via variable d'environnement)
PSM_URL = os.environ.get("POINT_SET_MANAGER_URL", "http://localhost:8000")


@app.route("/triangulation/<point_set_id>", methods=["GET"])
def get_triangulation(point_set_id):
    """
    Calcule la triangulation pour un ID de PointSet donné.

    Workflow :
        1. Valide l'ID du PointSet (doit être un UUID valide).
        2. Récupère les données binaires du PointSet depuis le PointSetManager.
        3. Convertit les données binaires en liste de points.
        4. Calcule la triangulation.
        5. Convertit le résultat au format binaire.
        6. Retourne la réponse binaire.

    Args:
        point_set_id: Chaîne UUID identifiant le PointSet.

    Returns:
        Réponse binaire (application/octet-stream) en cas de succès (200).
        Réponse d'erreur JSON en cas d'échec (400, 404, 500, 503).
    """
    # Validation du format UUID
    try:
        uuid.UUID(point_set_id)
    except ValueError:
        return (
            jsonify(
                {
                    "code": "INVALID_UUID",
                    "message": f"Format d'ID de PointSet invalide : {point_set_id}",
                }
            ),
            400,
        )

    # Récupération du PointSet depuis le PointSetManager
    try:
        psm_url = f"{PSM_URL}/pointset/{point_set_id}"
        response = requests.get(psm_url, timeout=10)

        # Gestion des erreurs du PointSetManager
        if response.status_code == 404:
            return (
                jsonify(
                    {
                        "code": "NOT_FOUND",
                        "message": f"PointSet avec l'ID {point_set_id} introuvable",
                    }
                ),
                404,
            )

        if response.status_code >= 500:
            return (
                jsonify(
                    {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": "Le service PointSetManager est indisponible",
                    }
                ),
                503,
            )

        if response.status_code != 200:
            return (
                jsonify(
                    {
                        "code": "POINTSET_MANAGER_ERROR",
                        "message": f"PointSetManager a retourné le status {response.status_code}",
                    }
                ),
                503,
            )

        pointset_binary = response.content

    except requests.exceptions.RequestException as e:
        return (
            jsonify(
                {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": f"Échec de communication avec PointSetManager : {str(e)}",
                }
            ),
            503,
        )

    # Décodage du PointSet binaire
    try:
        points = pointset_from_binary(pointset_binary)
    except (ValueError, Exception) as e:
        return (
            jsonify(
                {
                    "code": "INVALID_POINTSET",
                    "message": f"Échec du parsing des données binaires du PointSet : {str(e)}",
                }
            ),
            500,
        )

    # Calcul de la triangulation
    try:
        triangles = triangulate_pointset(points)
    except Exception as e:
        return (
            jsonify(
                {
                    "code": "TRIANGULATION_FAILED",
                    "message": f"Échec du calcul de triangulation : {str(e)}",
                }
            ),
            500,
        )

    # Encodage du résultat en binaire
    try:
        result_binary = triangles_to_binary(points, triangles)
    except Exception as e:
        return (
            jsonify(
                {
                    "code": "ENCODING_FAILED",
                    "message": f"Échec de l'encodage du résultat de triangulation : {str(e)}",
                }
            ),
            500,
        )

    # Retour de la réponse binaire
    return Response(result_binary, mimetype="application/octet-stream")


if __name__ == "__main__":
    app.run(debug=True)
