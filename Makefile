.PHONY: all
all: lint style

.PHONY: lint
lint:
	flake8

.PHONY: style
style:
	autopep8 -r -i src