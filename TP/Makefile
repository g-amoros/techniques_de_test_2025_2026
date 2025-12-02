.PHONY: install test unit_test perf_test coverage lint doc run clean

install:
	pip install -r requirements.txt -r dev_requirements.txt

# Lance tous les tests (unitaires + integration + perf)
test:
	pytest -v

# Lance uniquement les tests unitaires et d'intégration (exclut la perf)
unit_test:
	pytest -v -m "not performance"

# Lance uniquement les tests de performance
perf_test:
	pytest -v -m "performance"

# Génère le rapport de couverture (sur les tests unitaires/intégration)
coverage:
	coverage run -m pytest -m "not performance"
	coverage report -m
	coverage html

# Vérifie la qualité du code
lint:
	ruff check src tests

# Génère la documentation
doc:
	pdoc --html --output-dir docs --force src

# Lance le serveur de développement
run:
	flask --app src.app run --debug --port 5000

clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__
	rm -rf htmlcov
	rm -rf docs
	rm -f .coverage