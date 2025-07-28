.PHONY: all install-poetry install format lint test precommit clean help

SRC_DIRS := momento_buffconf_workshop tests
SRC_AND_NOTEBOOKS := $(SRC_DIRS) notebooks

## Generate sync unit tests, format, lint, and test
all: precommit

## Bootstrap installing poetry
install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -

## Install project and dependencies
install:
	@poetry install

## Format the code using ruff
format-fix:
	@poetry run ruff format $(SRC_AND_NOTEBOOKS)

## Check the code formatting using ruff
format-check:
	@poetry run ruff check $(SRC_AND_NOTEBOOKS)

## Fix linting errors
lint-fix:
	@poetry run ruff check $(SRC_AND_NOTEBOOKS)

## Check the lint the code using ruff and mypy
lint-check:
	@poetry run ruff check $(SRC_AND_NOTEBOOKS)
	@poetry run mypy $(SRC_DIRS)

## Run unit and integration tests with pytest
test:
	@poetry run pytest

## Run format, lint, and test as a step before committing.
precommit: gen-sync format lint test

## Remove intermediate files
clean:
	@rm -rf dist .mypy_cache .pytest_cache
	@find . -name "*__pycache__*" | xargs rm -rf


# See <https://gist.github.com/klmr/575726c7e05d8780505a> for explanation.
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)";echo;sed -ne"/^## /{h;s/.*//;:d" -e"H;n;s/^## //;td" -e"s/:.*//;G;s/\\n## /---/;s/\\n/ /g;p;}" ${MAKEFILE_LIST}|LC_ALL='C' sort -f|awk -F --- -v n=$$(tput cols) -v i=19 -v a="$$(tput setaf 6)" -v z="$$(tput sgr0)" '{printf"%s%*s%s ",a,-i,$$1,z;m=split($$2,w," ");l=n-i;for(j=1;j<=m;j++){l-=length(w[j])+1;if(l<= 0){l=n-i-length(w[j])-1;printf"\n%*s ",-i," ";}printf"%s ",w[j];}printf"\n";}'|more $(shell test $(shell uname) == Darwin && echo '-Xr')
