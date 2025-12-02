# PLAN.md - Plan de Tests pour le Triangulator

## 1. Objectif

Ce document décrit la stratégie de test pour le micro-service Triangulator. L'objectif est de valider la conformité fonctionnelle, la robustesse et les performances du service.

Outils principaux : pytest (exécution), unittest.mock (mocks), coverage (mesure de couverture).

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

#### b) Module `triangulator/logic.py`

**Tests pour `compute_triangulation` :**
- `test_compute_triangulation_square` : Cas nominal avec 4 points formant un carré → 2 triangles.
- `test_compute_triangulation_triangle` : Cas nominal avec 3 points formant un triangle → 1 triangle.
- `test_compute_triangulation_few_points` : Cas limite avec 0, 1, 2 points → retourner liste vide.
- `test_compute_triangulation_collinear` : Cas complexe avec des points colinéaires → retourner liste vide.
- `test_compute_triangulation_duplicates` : Cas complexe avec des points dupliqués → lever une ValueError.
- `test_compute_triangulation_concave` : Cas complexe avec un ensemble de points concaves → vérifier triangulation valide.

**Tests pour les fonctions privées (couverture complète) :**
- `test_point_in_triangle` : Test de la fonction `_point_in_triangle` (point intérieur, extérieur, sur le bord).
- `test_circumcircle_contains_collinear` : Test de `_circumcircle_contains` avec points colinéaires (d ≈ 0).

### 2.2 Tests d'intégration (API)

But : valider l'endpoint `/triangulation/<pointSetId>` en simulant PointSetManager. Utiliser `app.test_client()` avec `unittest.mock` pour mocker les appels HTTP.

**Tests du cas nominal :**
- `test_get_triangulation_success` (happy path)
  - Mock PointSetManager → renvoie données binaires valides (3 points).
  - Appel avec UUID valide.
  - Vérifier status_code 200, mimetype `application/octet-stream`.
  - Désérialiser la réponse et vérifier format Triangles.

**Tests de validation d'entrée :**
- `test_get_triangulation_invalid_uuid` : Appel avec `pointSetId` non UUID → vérifier status_code 400 et message d'erreur JSON.

**Tests d'erreurs du PointSetManager :**
- `test_get_triangulation_manager_404` : Mock PointSetManager → 404 → vérifier status_code 404 et message JSON.
- `test_get_triangulation_manager_400` : Mock PointSetManager → 400 → vérifier status_code 400 et message JSON.
- `test_get_triangulation_manager_500` : Mock PointSetManager → 500 → vérifier status_code 503 et message JSON.
- `test_get_triangulation_manager_503` : Mock PointSetManager → lève `ConnectionError` → vérifier status_code 503 et message JSON.
- `test_get_triangulation_timeout` : Mock PointSetManager → lève `Timeout` → vérifier status_code 503 et message JSON.
- `test_get_triangulation_request_exception` : Mock PointSetManager → lève `RequestException` → vérifier status_code 503 et message JSON.

**Tests d'erreurs internes :**
- `test_get_triangulation_parse_error` : Données binaires invalides → vérifier status_code 500 et message JSON.
- `test_get_triangulation_value_error` : Points dupliqués causant ValueError → vérifier status_code 500 et message JSON.
- `test_get_triangulation_serialization_error` : Erreur lors de la sérialisation → vérifier status_code 500 et message JSON.
- `test_get_triangulation_internal_error` : Erreur générique dans l'algorithme → vérifier status_code 500 et message JSON.
- `test_not_implemented_error_handler` : Test du handler `NotImplementedError` pour couverture complète.

### 2.3 Tests de performance

Marquer avec `@pytest.mark.perf` et exécuter séparément (ex. `make perf_test`).

**Tests de sérialisation :**
- `test_perf_parse_pointset` : Mesurer désérialisation pour 1, 10, 100 points.
- `test_perf_serialize_triangles` : Mesurer sérialisation pour 1, 10, 100 points.

**Tests de triangulation :**
- `test_perf_triangulation` : Mesurer calcul de triangulation pour 1, 10, 100 points.

**Note :** Les tailles ont été réduites à [1, 10, 100] pour permettre une exécution rapide tout en conservant la pertinence des mesures de performance.

## 3. Qualité de code et documentation

### 3.1 Linting
- Commande : `make lint` (ruff check)
- Objectif : Aucune erreur de linting
- Règles activées : D (docstrings), E (erreurs), F (erreurs fatales), UP (modernisation), B (bugs), SIM (simplification), I (imports)

### 3.2 Couverture de code
- Commande : `make coverage` (coverage run -m pytest -m "not perf")
- Objectif : Viser 100% sur `app.py`, `triangulator/logic.py`, `triangulator/serialization.py`
- Résultat actuel :
  - `app.py` : 99% (1 ligne non couverte : `if __name__ == '__main__'`)
  - `triangulator/logic.py` : 100%
  - `triangulator/serialization.py` : 100%
  - Total : 93%

### 3.3 Documentation
- Commande : `make doc` (pdoc3 --html --output-dir docs triangulator/)
- Objectif : Générer la documentation HTML utilisable à partir des docstrings

## 4. Structure du projet

```
TP/
├── app.py                          # Application Flask principale
├── triangulator/                   # Package principal
│   ├── __init__.py
│   ├── logic.py                    # Algorithme de triangulation
│   └── serialization.py            # Sérialisation/désérialisation binaire
├── tests/
│   ├── unit/                       # Tests unitaires
│   │   ├── test_logic.py          # Tests de la logique de triangulation
│   │   └── test_serialization.py  # Tests de sérialisation
│   ├── integration/                # Tests d'intégration
│   │   └── test_api.py            # Tests de l'API Flask
│   └── perf/                       # Tests de performance
│       ├── test_serialization_perf.py
│       └── test_triangulation_perf.py
├── Makefile                        # Commandes make pour les tests
├── requirements.txt                # Dépendances de production
├── dev_requirements.txt            # Dépendances de développement
└── pyproject.toml                  # Configuration ruff et pytest
```

## 5. Commandes d'exécution

### 5.1 Tests
- `make test` : Lance tous les tests (y compris performance)
- `make unit_test` : Lance tous les tests sauf les tests de performance
- `make perf_test` : Lance uniquement les tests de performance

### 5.2 Qualité
- `make coverage` : Génère un rapport de couverture de code (exclut les tests de performance)
- `make lint` : Valide la qualité de code avec ruff
- `make doc` : Génère la documentation en HTML

## 6. Résumé des tests implémentés

- **Tests unitaires** : 15 tests (8 pour logic, 7 pour serialization)
- **Tests d'intégration** : 13 tests (couverture complète des cas d'erreur)
- **Tests de performance** : 3 tests (sérialisation et triangulation)

**Total : 31 tests** (28 tests unitaires + intégration, 3 tests de performance)

---
