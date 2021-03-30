PHONY += all
all: style lint test

PHONY += lint
lint:
	flakehell lint src

PHONY += style
style:
	autopep8 -r -i src

PHONY += test
test:
	pytest src/tests

PHONY += report
report:
	pytest --cov-report html --cov=src src/tests/