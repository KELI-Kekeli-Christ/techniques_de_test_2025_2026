"""Module de logique pour le calcul de triangulation.

Ce module fournit l'algorithme principal pour :
- Calculer une triangulation à partir d'un ensemble de points
"""


def _cross_product(
    o: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float]
) -> float:
    """Fait le produit vectoriel (a - o) x (b - o).
    
    Args:
        o: Point origine
        a: Premier point
        b: Second point
    
    Returns:
        La valeur du produit vectoriel

    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _point_in_triangle(
    p: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float]
) -> bool:
    """Vérifie si un point est à l'intérieur d'un triangle.
    
    Args:
        p: Point à tester
        a: Premier sommet du triangle
        b: Deuxième sommet du triangle
        c: Troisième sommet du triangle
    
    Returns:
        True si le point est dans le triangle (ou sur le bord)

    """
    d1 = _cross_product(a, b, p)
    d2 = _cross_product(b, c, p)
    d3 = _cross_product(c, a, p)
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    
    return not (has_neg and has_pos)


def _circumcircle_contains(
    p: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float]
) -> bool:
    """Vérifie si un point est dans le cercle circonscrit d'un triangle.
    
    Args:
        p: Point à tester
        a: Premier sommet du triangle
        b: Deuxième sommet du triangle
        c: Troisième sommet du triangle
    
    Returns:
        True si le point est dans le cercle circonscrit

    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    px, py = p
    
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-10:
        return False
    
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) +
          (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) +
          (cx * cx + cy * cy) * (bx - ax)) / d
    
    r_sq = (ax - ux) ** 2 + (ay - uy) ** 2
    dist_sq = (px - ux) ** 2 + (py - uy) ** 2
    
    return dist_sq <= r_sq


def _is_duplicate(
    p1: tuple[float, float],
    p2: tuple[float, float],
    epsilon: float = 1e-10
) -> bool:
    """Vérifie si deux points sont identiques.
    
    Args:
        p1: Premier point à comparer
        p2: Deuxième point à comparer
        epsilon: Tolérance pour la comparaison
    
    Returns:
        True si les points sont identiques

    """
    return abs(p1[0] - p2[0]) < epsilon and abs(p1[1] - p2[1]) < epsilon


def _are_collinear(
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    epsilon: float = 1e-10
) -> bool:
    """Vérifie si trois points sont colinéaires.
    
    Args:
        p1: Premier point à vérifier
        p2: Deuxième point à vérifier
        p3: Troisième point à vérifier
        epsilon: Tolérance pour la comparaison
    
    Returns:
        True si les points sont colinéaires

    """
    return abs(_cross_product(p1, p2, p3)) < epsilon


def compute_triangulation(
    points: list[tuple[float, float]]
)-> list[tuple[int, int, int]]:
    """ 
    Triangule  un ensemble de points 2D.

    Utilise un algorithme de triangulation de Delaunay simplifié
    basé sur l'ajout incrémental de points.
    
    Args:
        points: Liste de tuples (x, y) représentant les points à trianguler
    
    Returns:
        Liste de tuples (i1, i2, i3) représentant les triangles,
        où i1, i2, i3 sont des indices dans la liste de points
    
    Raises:
        ValueError: Si des points sont invalides (ex: dupliqués)

    """
    # Cas limites
    if len(points) < 3:
        return []
    
    # Vérifier les doublons
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if _is_duplicate(points[i], points[j]):
                raise ValueError(f"Points dupliqués détectés: {points[i]}")
    
    # Si seulement 3 points et qu'ils ne sont pas colinéaires
    if len(points) == 3:
        if _are_collinear(points[0], points[1], points[2]):
            return []
        return [(0, 1, 2)]
    
    # Algorithme de triangulation incrémentale simplifiée
    # On utilise un super-triangle pour démarrer
    # Puis on ajoute les points un par un
    
    # Trouver les bornes
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    
    dx = max_x - min_x
    dy = max_y - min_y
    dmax = max(dx, dy)
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2
    
    # Super-triangle qui contient tous les points
    super_triangle = [
        (mid_x - 20 * dmax, mid_y - dmax),
        (mid_x + 20 * dmax, mid_y - dmax),
        (mid_x, mid_y + 20 * dmax)
    ]
    
    # Initialiser avec le super-triangle
    triangles = [(len(points), len(points) + 1, len(points) + 2)]
    extended_points = points + super_triangle
    
    # Ajouter chaque point
    for point_idx in range(len(points)):
        point = points[point_idx]
        
        # Trouver les triangles dont le cercle circonscrit contient le point
        bad_triangles = []
        for tri_idx, triangle in enumerate(triangles):
            a = extended_points[triangle[0]]
            b = extended_points[triangle[1]]
            c = extended_points[triangle[2]]
            
            if _circumcircle_contains(point, a, b, c):
                bad_triangles.append(tri_idx)
        
        # Trouver le polygone de la cavité
        edges = []
        for tri_idx in bad_triangles:
            tri = triangles[tri_idx]
            edges.append((tri[0], tri[1]))
            edges.append((tri[1], tri[2]))
            edges.append((tri[2], tri[0]))
        
        # Trouver les arêtes qui ne sont partagées qu'une fois
        edge_count = {}
        for edge in edges:
            edge_sorted = tuple(sorted(edge))
            edge_count[edge_sorted] = edge_count.get(edge_sorted, 0) + 1
        
        boundary_edges = [
            edge for edge, count in edge_count.items()
            if count == 1
        ]
        
        # Supprimer les mauvais triangles
        for tri_idx in sorted(bad_triangles, reverse=True):
            triangles.pop(tri_idx)
        
        # Créer de nouveaux triangles avec le nouveau point
        for edge in boundary_edges:
            triangles.append((edge[0], edge[1], point_idx))
    
    # Supprimer les triangles qui contiennent des sommets du super-triangle
    super_vertex_indices = {len(points), len(points) + 1, len(points) + 2}
    final_triangles = []
    for triangle in triangles:
        if not any(v in super_vertex_indices for v in triangle):
            final_triangles.append(triangle)
    
    return final_triangles