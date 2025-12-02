"""Tests de performance pour l'algorithme de triangulation."""

import random
import time

import pytest
from triangulator.logic import compute_triangulation


@pytest.mark.perf
def test_perf_triangulation():
    """Test les performances du calcul de triangulation."""
    sizes = [1, 10, 100]
    
    for size in sizes:
        # Création d'un ensemble de points aléatoires
        points = [
            (random.uniform(-1000, 1000), random.uniform(-1000, 1000))
            for _ in range(size)
        ]
        
        # Mesure du temps de triangulation
        start = time.perf_counter()
        triangles = compute_triangulation(points)
        duration = time.perf_counter() - start
        
        # Vérifications basiques
        assert isinstance(triangles, list)
        if triangles:  # Si des triangles ont été créés
            assert all(len(t) == 3 for t in triangles)
        
        print(f"compute_triangulation pour {size:,} points: {duration:.3f} secondes")