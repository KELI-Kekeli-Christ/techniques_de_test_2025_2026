"""Tests unitaires pour le module logic."""

import pytest
from triangulator.logic import (
    _circumcircle_contains,
    _point_in_triangle,
    compute_triangulation,
)


def test_compute_triangulation_square():
    """Test le cas nominal avec 4 points formant un carré."""
    points = [
        (0.0, 0.0),  # Coin bas-gauche
        (1.0, 0.0),  # Coin bas-droite
        (1.0, 1.0),  # Coin haut-droite
        (0.0, 1.0)   # Coin haut-gauche
    ]
    
    triangles = compute_triangulation(points)
    
    # Un carré doit être divisé en 2 triangles
    assert len(triangles) == 2
    
    # Vérifier que chaque triangle utilise 3 points distincts
    for triangle in triangles:
        assert len(triangle) == 3
        assert len(set(triangle)) == 3  # Pas de point en double
        assert all(0 <= i < len(points) for i in triangle)  # Indices valides

def test_compute_triangulation_triangle():
    """Test le cas nominal avec 3 points formant un triangle."""
    points = [
        (0.0, 0.0),
        (1.0, 0.0),
        (0.0, 1.0)
    ]
    
    triangles = compute_triangulation(points)
    
    # Un triangle doit donner... un triangle
    assert len(triangles) == 1
    assert len(triangles[0]) == 3
    assert all(0 <= i < 3 for i in triangles[0])

def test_compute_triangulation_few_points():
    """Test les cas limites avec 0, 1 ou 2 points."""
    assert compute_triangulation([]) == []  # 0 point
    assert compute_triangulation([(0.0, 0.0)]) == []  # 1 point
    assert compute_triangulation([(0.0, 0.0), (1.0, 1.0)]) == []  # 2 points

def test_compute_triangulation_collinear():
    """Test le cas complexe avec des points colinéaires."""
    points = [
        (0.0, 0.0),
        (1.0, 1.0),
        (2.0, 2.0)  # Points alignés
    ]
    
    triangles = compute_triangulation(points)
    assert len(triangles) == 0  # Pas de triangle possible avec points alignés

def test_compute_triangulation_duplicates():
    """Test le cas complexe avec des points dupliqués."""
    points = [
        (0.0, 0.0),
        (1.0, 0.0),
        (0.0, 1.0),
        (0.0, 0.0)  # Point dupliqué
    ]
    
    # Doit lever une exception ou ignorer les doublons
    with pytest.raises(ValueError):
        compute_triangulation(points)

def test_compute_triangulation_concave():
    """Test le cas complexe avec un ensemble de points concaves."""
    points = [
        (0.0, 0.0),   # 0
        (1.0, 0.0),   # 1
        (2.0, 0.0),   # 2
        (2.0, 1.0),   # 3
        (1.0, 0.5),   # 4 (point concave)
        (0.0, 1.0)    # 5
    ]
    
    triangles = compute_triangulation(points)
    
    # Vérifier que nous avons une triangulation valide
    assert len(triangles) >= 4  # Au moins 4 triangles pour cette forme
    
    # Vérifier que chaque triangle est valide
    for triangle in triangles:
        assert len(triangle) == 3
        assert len(set(triangle)) == 3
        assert all(0 <= i < len(points) for i in triangle)

def test_point_in_triangle():
    """Test de la fonction _point_in_triangle pour couverture."""
    # Point à l'intérieur
    assert _point_in_triangle((0.5, 0.5), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)) is True
    # Point à l'extérieur
    assert _point_in_triangle((2.0, 2.0), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)) is False
    # Point sur le bord
    assert _point_in_triangle((0.5, 0.0), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)) is True

def test_circumcircle_contains_collinear():
    """Test _circumcircle_contains avec points colinéaires (d = 0)."""
    # Points colinéaires : d sera très proche de 0
    result = _circumcircle_contains(
        (1.0, 1.0),  # Point à tester
        (0.0, 0.0),  # Points colinéaires
        (1.0, 1.0),
        (2.0, 2.0)
    )
    assert result is False  # Doit retourner False quand d ≈ 0