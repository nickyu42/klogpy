PROJECT_DIR := klogpy

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