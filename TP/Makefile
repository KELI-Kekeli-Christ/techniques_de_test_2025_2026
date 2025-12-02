# Makefile pour le projet Triangulator

.PHONY: test unit_test perf_test coverage lint doc

# Lance tous les tests
test:
	pytest

# Lance uniquement les tests unitaires et d'intégration
unit_test:
	pytest -v -m "not perf"

# Lance uniquement les tests de performance
perf_test:
	pytest -v -m perf

# Génère le rapport de couverture
coverage:
	coverage run -m pytest 
	coverage report
	coverage html

# Vérifie la qualité du code
lint:
	ruff check .

# Génère la documentation
doc:
	pdoc3 --html --output-dir docs triangulator/