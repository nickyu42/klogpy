.PHONY: all
all: lint style

.PHONY: lint
lint:
	flake8 *.py

.PHONY: style
style:
	autopep8 -r -i .