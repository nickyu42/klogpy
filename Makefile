PROJECT_DIR := klogpy
include .env

PHONY += all
all: style lint test

PHONY += lint
lint:
	flakehell lint $(PROJECT_DIR)

PHONY += style
style:
	autopep8 -r --max-line-length 119 -i $(PROJECT_DIR)

PHONY += test
test:
	pytest tests

PHONY += cov-report
cov-report:
	pytest --cov-report html --cov=$(PROJECT_DIR) tests

PHONY += publish
publish:
	poetry publish --build --username $(PYPI_USERNAME) --password $(PYPI_PASSWORD)
