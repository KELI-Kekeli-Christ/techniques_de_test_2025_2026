"""Module de sérialisation pour les formats binaires PointSet et Triangles.

Ce module fournit les fonctions pour :
- Parser des données binaires PointSet
- Sérialiser des triangles en format binaire
"""

import struct


def parse_pointset_binary(data: bytes) -> list[tuple[float, float]]:
    """Parse les données binaires d'un PointSet.
    
    Args:
        data: Les données binaires au format PointSet
             (4 bytes nb_points + nb_points * 8 bytes de coordonnées)
    
    Returns:
        Liste de tuples (x, y) représentant les points
    
    Raises:
        ValueError: Si les données sont corrompues ou de format invalide

    """
    if len(data) < 4:
        raise ValueError("Données insuffisantes pour lire le nombre de points")
    
    # Lire le nombre de points (4 bytes, unsigned long, little-endian)
    num_points = struct.unpack('<L', data[:4])[0]
    
    # Vérifier que nous avons assez de données
    expected_size = 4 + (num_points * 8)
    if len(data) < expected_size:
        raise ValueError(
            f"Données insuffisantes: attendu {expected_size} bytes, "
            f"reçu {len(data)} bytes"
        )
    
    # Parser les points
    points = []
    offset = 4
    for _ in range(num_points):
        x, y = struct.unpack('<ff', data[offset:offset+8])
        points.append((x, y))
        offset += 8
    
    return points


def serialize_triangles_binary(
    points: list[tuple[float, float]], 
    triangles: list[tuple[int, int, int]]
) -> bytes:
    """Sérialise des points et triangles au format binaire Triangles.
    
    Args:
        points: Liste de tuples (x, y) représentant les points
        triangles: Liste de tuples (i1, i2, i3) d'indices de points
    
    Returns:
        Les données au format binaire Triangles
    
    Raises:
        ValueError: Si les indices de triangles sont invalides

    """
    num_points = len(points)
    num_triangles = len(triangles)
    
    # Vérifier que tous les indices sont valides
    for triangle in triangles:
        i1, i2, i3 = triangle
        if not (0 <= i1 < num_points and 0 <= i2 < num_points and 0 <= i3 < num_points):
            raise ValueError(
                f"Indice invalide dans le triangle {triangle}: "
                f"les indices doivent être entre 0 et {num_points - 1}"
            )
    
    # Construire les données binaires
    data = bytearray()
    
    # Partie 1: Points (format PointSet)
    data.extend(struct.pack('<L', num_points))
    for x, y in points:
        data.extend(struct.pack('<ff', x, y))
    
    # Partie 2: Triangles
    data.extend(struct.pack('<L', num_triangles))
    for i1, i2, i3 in triangles:
        data.extend(struct.pack('<LLL', i1, i2, i3))
    
    return bytes(data)