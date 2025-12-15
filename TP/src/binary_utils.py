"""Utilitaires d'encodage et décodage binaire pour PointSet et Triangles."""

import struct


def pointset_from_binary(data: bytes) -> list[tuple[float, float]]:
    """Convertit un blob binaire (PointSet) en liste de tuples (x, y).

    Format binaire attendu :
        - 4 bytes (unsigned long) : Nombre de points (N)
        - N * 8 bytes : Données des points, où chaque point est :
            - 4 bytes (float) : Coordonnée X
            - 4 bytes (float) : Coordonnée Y

    Args:
        data: Représentation binaire d'un PointSet.

    Returns:
        Liste de tuples de coordonnées (x, y).

    Raises:
        ValueError: Si les données binaires sont malformées ou tronquées.

    """
    if len(data) < 4:
        raise ValueError("Données binaires trop courtes : nombre de points manquant")

    # Lecture du nombre de points (unsigned long, little endian)
    count = struct.unpack("<L", data[:4])[0]

    # Taille attendue : 4 bytes (count) + count * 8 bytes (2 floats par point)
    expected_size = 4 + count * 8
    if len(data) != expected_size:
        raise ValueError(
            f"Taille binaire invalide : attendu {expected_size} bytes, reçu {len(data)}"
        )

    points = []
    offset = 4

    for _ in range(count):
        # La vérification de taille est déjà faite par expected_size,
        # on peut lire directement en toute sécurité.
        x, y = struct.unpack("<ff", data[offset : offset + 8])
        points.append((x, y))
        offset += 8

    return points


def triangles_to_binary(
    points: list[tuple[float, float]], triangles: list[tuple[int, int, int]]
) -> bytes:
    """Convertit les points et triangles en représentation binaire.

    Format binaire :
        Partie 1 - Sommets (format PointSet) :
            - 4 bytes (unsigned long) : Nombre de sommets (N)
            - N * 8 bytes : Données des sommets (2 floats par sommet)

        Partie 2 - Triangles :
            - 4 bytes (unsigned long) : Nombre de triangles (T)
            - T * 12 bytes : Indices des triangles (3 unsigned longs par triangle)

    Args:
        points: Liste de tuples de coordonnées (x, y).
        triangles: Liste de tuples d'indices (idx1, idx2, idx3).

    Returns:
        Représentation binaire de la structure Triangles.

    Raises:
        ValueError: Si les indices des triangles sont hors limites.

    """
    # Validation des indices des triangles
    num_points = len(points)
    for tri in triangles:
        for idx in tri:
            if idx < 0 or idx >= num_points:
                raise ValueError(
                    f"Indice de triangle {idx} hors limites (0-{num_points - 1})"
                )

    # Partie 1 : Encodage du PointSet
    result = bytearray()

    # Nombre de points
    result.extend(struct.pack("<L", len(points)))

    # Coordonnées des points
    for x, y in points:
        result.extend(struct.pack("<ff", x, y))

    # Partie 2 : Encodage des Triangles
    # Nombre de triangles
    result.extend(struct.pack("<L", len(triangles)))

    # Indices des triangles
    for idx1, idx2, idx3 in triangles:
        result.extend(struct.pack("<LLL", idx1, idx2, idx3))

    return bytes(result)