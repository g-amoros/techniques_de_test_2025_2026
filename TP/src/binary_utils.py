import struct

def pointset_from_binary(data: bytes) -> list[tuple[float, float]]:
    """
    Convertit un blob binaire (PointSet) en liste de tuples (x, y).
    Format: 4 bytes (unsigned long) count + count * 8 bytes (2 floats).
    """
    # TODO: Implémenter le parsing binaire
    raise NotImplementedError("Parsing binaire non implémenté")

def triangles_to_binary(points: list[tuple[float, float]], triangles: list[tuple[int, int, int]]) -> bytes:
    """
    Convertit la liste des points et des triangles en blob binaire.
    Format: PointSet binary + 4 bytes (count) + count * 12 bytes (3 unsigned long).
    """
    # TODO: Implémenter l'écriture binaire
    raise NotImplementedError("Encodage binaire non implémenté")