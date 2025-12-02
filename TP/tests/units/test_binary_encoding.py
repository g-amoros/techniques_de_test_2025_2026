import struct
import pytest
from src.binary_utils import pointset_from_binary, triangles_to_binary

def test_read_pointset_nominal():
    # Création manuelle d'un binaire valide : 2 points (0,0) et (1,1)
    count = 2
    p1 = (0.0, 0.0)
    p2 = (1.0, 1.0)
    data = struct.pack('<L', count) + struct.pack('<ffff', p1[0], p1[1], p2[0], p2[1])
    
    # Appel de la fonction (devrait échouer car NotImplemented)
    result = pointset_from_binary(data)
    
    assert len(result) == 2
    assert result[0] == p1
    assert result[1] == p2

def test_read_pointset_empty():
    data = struct.pack('<L', 0)
    result = pointset_from_binary(data)
    assert result == []

def test_read_pointset_invalid_size():
    # Données tronquées (manque un bout de coordonnée)
    data = struct.pack('<L', 1) + struct.pack('<f', 0.0) 
    with pytest.raises(ValueError): # Ou struct.error
        pointset_from_binary(data)

def test_write_triangles_nominal():
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles = [(0, 1, 2)]
    
    binary_data = triangles_to_binary(points, triangles)
    
    # Vérification basique de la taille : 
    # PointSet part: 4 (nb points) + 3*8 (coords) = 28 bytes
    # Triangle part: 4 (nb tri) + 1*12 (indices) = 16 bytes
    # Total = 44 bytes
    assert len(binary_data) == 44