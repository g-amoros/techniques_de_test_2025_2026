import pytest
import time
import random
from src.core import triangulate_pointset

@pytest.mark.performance
def test_large_dataset_performance():
    # Génération de 1000 points aléatoires
    points = [(random.random(), random.random()) for _ in range(1000)]
    
    start_time = time.time()
    try:
        triangulate_pointset(points)
    except NotImplementedError:
        pytest.fail("Algorithme non implémenté, impossible de tester la perf")
    
    duration = time.time() - start_time
    
    # Critère d'acceptation (ex: < 1 seconde pour 1000 points)
    assert duration < 1.0