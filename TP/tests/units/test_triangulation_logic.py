"""Tests unitaires pour la logique de triangulation."""

from src.core import _in_circumcircle, triangulate_pointset


def test_triangulation_simple_square():
    """Teste la triangulation d'un carré simple (4 points)."""
    # Carré avec 4 points
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    result = triangulate_pointset(points)

    # On attend 2 triangles pour un carré
    assert len(result) == 2

    # Vérification que les indices sont valides
    for t in result:
        assert len(t) == 3
        assert all(0 <= idx < 4 for idx in t)


def test_triangulation_collinear():
    """Teste le cas de points alignés (doit retourner vide)."""
    # 3 points alignés -> pas de triangle possible ou triangle plat géré
    points = [(0, 0), (1, 1), (2, 2)]
    result = triangulate_pointset(points)
    # Selon l'implémentation, soit 0 triangles, soit une exception, soit ignoré
    # Ici on suppose qu'on veut 0 triangles
    assert len(result) == 0


def test_triangulation_not_enough_points():
    """Teste le cas avec moins de 3 points."""
    points = [(0, 0), (1, 1)]
    result = triangulate_pointset(points)
    assert len(result) == 0


def test_triangulation_duplicates():
    """Teste la gestion des points dupliqués."""
    # Points dupliqués - notre implémentation les supprime automatiquement
    points = [(0, 0), (0, 0), (1, 1)]
    result = triangulate_pointset(points)
    # Avec seulement 2 points uniques, pas de triangulation possible
    assert len(result) == 0


def test_triangulation_duplicates_with_valid_triangle():
    """Teste des points dupliqués formant tout de même un triangle valide."""
    # Points dupliqués mais avec assez de points uniques pour une triangulation
    points = [(0, 0), (0, 0), (1, 0), (1, 0), (0.5, 1)]
    result = triangulate_pointset(points)
    # Devrait avoir 1 triangle avec les 3 points uniques
    assert len(result) == 1
    # Vérification que les indices sont valides (référencent les points originaux)
    for t in result:
        assert len(t) == 3
        assert all(0 <= idx < len(points) for idx in t)


def test_internal_in_circumcircle_degenerate():
    """Teste la fonction interne _in_circumcircle avec un triangle dégénéré."""
    # Triangle plat (dégénéré)
    p_flat_tri = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    tri_indices = (0, 1, 2)
    test_point = (3.0, 3.0)

    # Doit retourner False car le calcul du cercle échoue/n'a pas de sens
    assert _in_circumcircle(test_point, tri_indices, p_flat_tri) is False