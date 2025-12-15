"""Tests de performance pour la triangulation."""

import random
import time

import pytest

from src.core import triangulate_pointset


@pytest.mark.performance
def test_large_dataset_performance():
    """Mesure le temps de triangulation sur un jeu de données de 1000 points."""
    # Génération de 1000 points aléatoires
    points = [(random.random(), random.random()) for _ in range(1000)]

    start_time = time.time()
    
    # Appel direct, plus besoin de try/except car l'algo est implémenté
    triangulate_pointset(points)

    duration = time.time() - start_time

    # Critère d'acceptation pour Python pur
    assert duration < 5.0