import pytest
from src.core import triangulate_pointset

def test_triangulation_simple_square():
    # Carré avec 4 points
    points = [(0,0), (1,0), (1,1), (0,1)]
    result = triangulate_pointset(points)
    
    # On attend 2 triangles pour un carré
    assert len(result) == 2
    
    # Vérification que les indices sont valides
    for t in result:
        assert len(t) == 3
        assert all(0 <= idx < 4 for idx in t)

def test_triangulation_collinear():
    # 3 points alignés -> pas de triangle possible ou triangle plat géré
    points = [(0,0), (1,1), (2,2)]
    result = triangulate_pointset(points)
    # Selon l'implémentation, soit 0 triangles, soit une exception, soit ignoré
    # Ici on suppose qu'on veut 0 triangles
    assert len(result) == 0

def test_triangulation_duplicates():
    # Points dupliqués
    points = [(0,0), (0,0), (1,1)]
    with pytest.raises(Exception): # Ou assertion sur le résultat nettoyé
        triangulate_pointset(points)