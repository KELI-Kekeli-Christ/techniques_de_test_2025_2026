# PLAN.md - Plan de Tests pour le Triangulator

## 1. Objectif

Ce document décrit la stratégie de test pour le micro-service Triangulator. L'objectif est de valider la conformité fonctionnelle, la robustesse et les performances du service.

Outils principaux : pytest (exécution), pytest-mock (mocks), coverage (mesure de couverture).

## 2. Catégories de tests

### 2.1 Tests unitaires (logique métier)

But : valider les composants internes isolément.

a) Module `serialization.py` (à créer)  
- test_parse_pointset_binary  
  - Cas nominal : 3 points — vérifier nombre et coordonnées (X,Y).  
  - Cas limite : 0 point.  
  - Cas limite : 1 point.  
  - Cas d'erreur : données binaires corrompues (longueur incorrecte) → lever une exception.

- test_serialize_triangles_binary  
  - Cas nominal : 1 triangle (3 points) — vérifier en-têtes (nb points, nb triangles), points et indices.  
  - Cas limite : 0 triangle.  
  - Cas d'erreur : indices référant des points inexistants → lever une exception.

b) Module `logic.py` (à créer)  
- test_compute_triangulation  
  - Cas nominal : carré (4 points) → 2 triangles.  
  - Cas nominal : triangle (3 points) → 1 triangle.  
  - Cas limite : 0, 1, 2 points → retourner liste vide.  
  - Cas complexe : points colinéaires.  
  - Cas complexe : points dupliqués.  
  - Cas complexe : ensemble concave (cf. triangulation.png).

### 2.2 Tests de comportement (API / intégration)

But : valider l'endpoint `/triangulation/<pointSetId>` en simulant PointSetManager. Utiliser `app.test_client()` ou `pytest-flask`.

- test_get_triangulation_success (happy path)  
  - Mock PointSetManager → renvoie données binaires valides (ex. 3 points).  
  - Appel avec UUID valide.  
  - Vérifier status_code 200, mimetype `application/octet-stream`.  
  - Désérialiser la réponse et vérifier format Triangles.

- test_get_triangulation_invalid_uuid  
  - Appel avec `pointSetId` non UUID (ex. "123").  
  - Vérifier status_code 400 et message d'erreur JSON.

- test_get_triangulation_manager_404  
  - Mock PointSetManager → 404.  
  - Appel avec UUID valide.  
  - Vérifier status_code 404 et message JSON.

- test_get_triangulation_manager_503  
  - Mock PointSetManager → lève `ConnectionError`.  
  - Vérifier status_code 503 et message JSON.

- test_get_triangulation_internal_error  
  - Simuler erreur dans l'algorithme (ex. `Exception("Erreur calcul")`).  
  - Vérifier status_code 500 et message JSON.

### 2.3 Tests de performance

Marquer avec `@pytest.mark.perf` et exécuter séparément (ex. `make perf_test`).

- test_perf_serialization  
  - Mesurer sérialisation/désérialisation pour 10, 1 000, 1 000 000 points.

- test_perf_triangulation  
  - Mesurer calcul pour 10, 1 000, 10 000 points.

## 3. Qualité de code et documentation

- Linting : `make lint` (ruff) doit passer sans erreur.  
- Couverture : `make coverage` (coverage run -m pytest) — viser 100% sur `app.py`, `logic.py`, `serialization.py`.  
- Documentation : `make doc` (pdoc3) doit générer la doc HTML utilisable.

## 4. Exécution

- Structure:  
  - `services/serialization.py`  
  - `services/logic.py`  
  - `services/app.py` (Flask)  
  - `tests/serialization/` (tests de serialization)  
  - `tests/triangulation/` (tests de triangulation)  
  - `tests/Api/` (tests d'API, mocks PointSetManager)  
  - `tests/perf/` (marqués `@pytest.mark.perf`)


---
