.PHONY: all
all: style lint

.PHONY: lint
lint:
	flakehell lint src

.PHONY: style
style:
	autopep8 -r -i src
