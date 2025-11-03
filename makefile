PYTHON = "python3.12"

# code to
format:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format .

# code linting
lint:
	$(PYTHON) -m ruff check .

# code testing
test:
	$(PYTHON) -m pytest tests/

build:
	$(PYTHON) setup.py sdist bdist_wheel

publish:
	$(PYTHON) -m twine upload dist/*

clean:
	$(RM) -rf dist build
	$(RM) -rf **/__pycache__ # remove all __pycache__ directories
	$(RM) -rf **/**/__pycache__ # remove all __pycache__ directories
	$(RM) -rf .pytest_cache
	$(RM) -rf .ruff_cache
	$(RM) -rf .mypy_cache
	$(RM) -rf .pytest_cache
	$(RM) -rf gspace.egg-info

pycache-clean:
	$(RM) -rf **/__pycache__ # remove all __pycache__ directories
	$(RM) -rf **/**/__pycache__ # remove all __pycache__ directories
