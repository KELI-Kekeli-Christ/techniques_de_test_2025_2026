"""Tests unitaires pour le module serialization."""

import struct

import pytest
from triangulator.serialization import parse_pointset_binary, serialize_triangles_binary


def test_parse_pointset_binary_nominal():
    """Test le cas nominal avec 3 points."""
    # Création des données binaires pour 3 points (little-endian)
    data = struct.pack('<L', 3)  # Nombre de points
    data += struct.pack('<ff', 0.0, 0.0)  # Point 1
    data += struct.pack('<ff', 1.0, 0.0)  # Point 2
    data += struct.pack('<ff', 0.0, 1.0)  # Point 3
    
    points = parse_pointset_binary(data)
    assert len(points) == 3
    assert points[0] == (0.0, 0.0)
    assert points[1] == (1.0, 0.0)
    assert points[2] == (0.0, 1.0)

def test_parse_pointset_binary_empty():
    """Test le cas limite avec 0 point."""
    data = struct.pack('<L', 0)
    points = parse_pointset_binary(data)
    assert len(points) == 0

def test_parse_pointset_binary_corrupt():
    """Test le cas d'erreur avec des données corrompues."""
    with pytest.raises(ValueError):
        parse_pointset_binary(b'invalid data')

def test_parse_pointset_binary_insufficient_data():
    """Test le cas d'erreur avec moins de 4 bytes (pas assez pour lire le nombre)."""
    with pytest.raises(ValueError, match="lire le nombre de points"):
        parse_pointset_binary(b'abc')  # Seulement 3 bytes

def test_serialize_triangles_binary_nominal():
    """Test le cas nominal avec 1 triangle."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangles = [(0, 1, 2)]  # Un triangle utilisant les 3 points
    
    binary = serialize_triangles_binary(points, triangles)
    
    # Vérification du format binaire (little-endian)
    num_points = struct.unpack('<L', binary[:4])[0]
    assert num_points == 3
    
    # Vérification des points
    offset = 4
    for i in range(3):
        x, y = struct.unpack('<ff', binary[offset:offset+8])
        assert (x, y) == points[i]
        offset += 8
    
    # Vérification des triangles
    num_triangles = struct.unpack('<L', binary[offset:offset+4])[0]
    assert num_triangles == 1
    
    # Vérification des indices du triangle
    offset += 4
    i1, i2, i3 = struct.unpack('<LLL', binary[offset:offset+12])
    assert (i1, i2, i3) == triangles[0]

def test_serialize_triangles_binary_empty():
    """Test le cas limite avec 0 triangle."""
    points = [(0.0, 0.0), (1.0, 0.0)]
    triangles = []
    
    binary = serialize_triangles_binary(points, triangles)
    num_points = struct.unpack('<L', binary[:4])[0]
    assert num_points == 2
    
    offset = 4 + (num_points * 8)  # Skip points data
    num_triangles = struct.unpack('<L', binary[offset:offset+4])[0]
    assert num_triangles == 0

def test_serialize_triangles_binary_invalid_index():
    """Test le cas d'erreur avec des indices invalides."""
    points = [(0.0, 0.0)]
    triangles = [(0, 1, 2)]  # Indices hors limites
    
    with pytest.raises(ValueError):
        serialize_triangles_binary(points, triangles)