"""Tests de performance pour les opérations de sérialisation."""

import random
import struct
import time

import pytest
from triangulator.serialization import parse_pointset_binary, serialize_triangles_binary


@pytest.mark.perf
def test_perf_parse_pointset():
    """Test les performances de la désérialisation de PointSet."""
    sizes = [1, 10, 100]
    
    for size in sizes:
        # Création des données de test (little-endian)
        data = struct.pack('<L', size)  # Nombre de points
        for _ in range(size):
            x = random.uniform(-1000, 1000)
            y = random.uniform(-1000, 1000)
            data += struct.pack('<ff', x, y)
        
        # Mesure du temps de désérialisation
        start = time.perf_counter()
        points = parse_pointset_binary(data)
        duration = time.perf_counter() - start
        
        assert len(points) == size
        print(f"parse_pointset_binary pour {size:,} points: {duration:.3f} secondes")

@pytest.mark.perf
def test_perf_serialize_triangles():
    """Test les performances de la sérialisation de Triangles."""
    sizes = [1, 10, 100]
    
    for size in sizes:
        # Création des données de test
        points = [
            (random.uniform(-1000, 1000), random.uniform(-1000, 1000))
            for _ in range(size)
        ]
        
        # Création de triangles (un triangle pour chaque groupe de 3 points)
        triangles = [
            (i, (i+1)%size, (i+2)%size)
            for i in range(0, size-2, 3)
        ]
        
        # Mesure du temps de sérialisation
        start = time.perf_counter()
        binary = serialize_triangles_binary(points, triangles)
        duration = time.perf_counter() - start
        
        # Vérification basique du format (little-endian)
        num_points = struct.unpack('<L', binary[:4])[0]
        assert num_points == size
        msg = f"serialize_triangle_binary pour {size:,} points: {duration:.3f} secondes"
        print(msg)