PHONY += all
all: style lint test

PHONY += lint
lint:
	flakehell lint src

PHONY += style
style:
	autopep8 -r --max-line-length 119 -i src

PHONY += test
test:
	pytest src/tests

PHONY += report
report:
	pytest --cov-report html --cov=src src/tests/