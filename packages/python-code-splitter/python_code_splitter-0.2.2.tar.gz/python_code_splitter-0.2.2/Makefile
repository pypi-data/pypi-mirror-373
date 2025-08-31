VENV_PATH = .venv

PACKAGE_NAME = python-code-splitter

TESTPYPI_REPOSITORY = https://test.pypi.org/legacy/

.PHONY: install update shell fmt build upload prod-upload clean

install:
	uv sync --dev

update:
	uv lock --upgrade

shell:
	python -m venv $(VENV_PATH)
	sh $(VENV_PATH)/bin/activate

fmt:
	isort .
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place .
	ruff format .
	ruff check . --fix

build: clean
	$(VENV_PATH)/bin/python -m build

# NOTE: check ~/.pypirc is configured correctly
upload:
	uv run twine upload --verbose --repository testpypi dist/*

prod-upload:
	uv run twine upload --verbose --repository pypi dist/*

clean:
	rm -rf dist