import pytest
from triangulator_service.logic import compute_triangulation

def test_triangulation_minimal():
    """Teste la triangulation avec 3 points (doit retourner 1 triangle)."""
    pytest.fail("Test non implémenté (Rendu 2)")

def test_triangulation_square():
    """Teste avec 4 points (doit retourner 2 triangles)."""
    pytest.fail("Test non implémenté (Rendu 2)")

def test_triangulation_collinear():
    """Teste avec des points alignés (cas limite)."""
    pytest.fail("Test non implémenté (Rendu 2)")

def test_triangulation_insufficient_points():
    """Teste avec 0, 1, ou 2 points (aucun triangle)."""
    pytest.fail("Test non implémenté (Rendu 2)")