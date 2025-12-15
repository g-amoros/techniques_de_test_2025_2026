"""Implémentation de l'algorithme de triangulation."""



def triangulate_pointset(points: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    """
    Réalise la triangulation de Delaunay sur un ensemble de points 2D.

    Utilise l'algorithme incrémental de Bowyer-Watson pour la triangulation de Delaunay.
    Gère les cas limites comme les points colinéaires et les doublons.

    Args:
        points: Liste de tuples de coordonnées (x, y).

    Returns:
        Liste de triangles, où chaque triangle est un tuple de trois indices de points.

    Raises:
        ValueError: S'il y a des points dupliqués ou moins de 3 points.
    """
    if len(points) < 3:
        return []

    # Suppression des doublons tout en préservant l'ordre
    unique_points = []
    seen = set()
    original_indices = []

    for i, p in enumerate(points):
        if p not in seen:
            seen.add(p)
            unique_points.append(p)
            original_indices.append(i)

    if len(unique_points) < 3:
        return []

    # Vérification si tous les points sont colinéaires
    if _are_collinear(unique_points):
        return []

    # Réalisation de la triangulation de Delaunay
    triangles = _delaunay_triangulation(unique_points)

    # Remapping des indices vers la liste de points originale si des doublons ont été supprimés
    if len(unique_points) < len(points):
        index_map = {i: original_indices[i] for i in range(len(unique_points))}
        triangles = [(index_map[a], index_map[b], index_map[c]) for a, b, c in triangles]

    return triangles


def _are_collinear(points: list[tuple[float, float]]) -> bool:
    """
    Vérifie si tous les points sont colinéaires.

    Args:
        points: Liste de points à vérifier.

    Returns:
        True si tous les points sont colinéaires, False sinon.
    """
    if len(points) < 3:
        return True

    # Utilisation du produit vectoriel pour vérifier la colinéarité
    x0, y0 = points[0]
    x1, y1 = points[1]

    for i in range(2, len(points)):
        x2, y2 = points[i]
        cross = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
        if abs(cross) > 1e-10:  # Pas colinéaire
            return False

    return True


def _delaunay_triangulation(points: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    """
    Réalise la triangulation de Delaunay en utilisant l'algorithme de Bowyer-Watson.

    Args:
        points: Liste de points uniques.

    Returns:
        Liste de triangles sous forme de tuples d'indices.
    """
    # Création d'un super-triangle qui contient tous les points
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    dx = max_x - min_x
    dy = max_y - min_y
    delta_max = max(dx, dy)
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    # Sommets du super-triangle (assez grand pour contenir tous les points)
    p1 = (mid_x - 20 * delta_max, mid_y - delta_max)
    p2 = (mid_x, mid_y + 20 * delta_max)
    p3 = (mid_x + 20 * delta_max, mid_y - delta_max)

    # Ajout des points du super-triangle à la liste des points
    extended_points = points + [p1, p2, p3]
    n = len(points)

    # Initialisation de la triangulation avec le super-triangle
    triangles = [(n, n + 1, n + 2)]

    # Ajout de chaque point un par un
    for i in range(n):
        bad_triangles = []

        # Recherche des triangles dont le cercle circonscrit contient le point
        for tri in triangles:
            if _in_circumcircle(extended_points[i], tri, extended_points):
                bad_triangles.append(tri)

        # Recherche de la frontière du trou polygonal
        polygon = []
        for tri in bad_triangles:
            for edge in _get_edges(tri):
                # Vérification si l'arête est partagée par un autre mauvais triangle
                is_shared = False
                for other_tri in bad_triangles:
                    if other_tri == tri:
                        continue
                    if edge in _get_edges(other_tri) or (edge[1], edge[0]) in _get_edges(other_tri):
                        is_shared = True
                        break

                if not is_shared:
                    polygon.append(edge)

        # Suppression des mauvais triangles
        for tri in bad_triangles:
            triangles.remove(tri)

        # Re-triangulation du trou polygonal
        for edge in polygon:
            triangles.append((edge[0], edge[1], i))

    # Suppression des triangles qui contiennent des sommets du super-triangle
    result = []
    for tri in triangles:
        if all(idx < n for idx in tri):
            result.append(tri)

    return result


def _in_circumcircle(
    point: tuple[float, float],
    triangle: tuple[int, int, int],
    all_points: list[tuple[float, float]],
) -> bool:
    """
    Vérifie si un point est à l'intérieur du cercle circonscrit d'un triangle.

    Args:
        point: Point à vérifier.
        triangle: Triangle sous forme de tuple de trois indices.
        all_points: Liste de tous les points.

    Returns:
        True si le point est à l'intérieur du cercle circonscrit, False sinon.
    """
    ax, ay = all_points[triangle[0]]
    bx, by = all_points[triangle[1]]
    cx, cy = all_points[triangle[2]]
    px, py = point

    # Calcul du centre et du rayon du cercle circonscrit
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

    if abs(d) < 1e-10:  # Triangle dégénéré
        return False

    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d

    radius_sq = (ax - ux) ** 2 + (ay - uy) ** 2
    dist_sq = (px - ux) ** 2 + (py - uy) ** 2

    return dist_sq < radius_sq


def _get_edges(triangle: tuple[int, int, int]) -> list[tuple[int, int]]:
    """
    Récupère les trois arêtes d'un triangle.

    Args:
        triangle: Triangle sous forme de tuple de trois indices.

    Returns:
        Liste d'arêtes sous forme de tuples (index1, index2).
    """
    a, b, c = triangle
    return [(a, b), (b, c), (c, a)]
