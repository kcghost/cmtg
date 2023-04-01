.PHONY: all install test-install upload clean

NAME    := $(shell awk -F "=" '/^name/ {gsub(/[ "]/,""); print $$2}' pyproject.toml)
VERSION := $(shell awk -F "=" '/^version/ {gsub(/[ "]/,""); print $$2}' pyproject.toml)
SRC     := $(shell find src/ -type f) pyproject.toml
WHEEL   := dist/$(NAME)-$(VERSION)-py3-none-any.whl
SDIST   := dist/$(NAME)-$(VERSION).tar.gz

SHELL := /bin/bash
.SHELLFLAGS = -ce
.ONESHELL:

all: $(WHEEL) $(SDIST)

$(WHEEL): $(SRC)
	python3 -m build -w

$(SDIST): $(SRC)
	python3 -m build -s

install: $(WHEEL)
	pip3 install --force-reinstall $(WHEEL)

test-install: $(WHEEL)
	$(RM) -r venv
	python3 -m venv venv
	source venv/bin/activate
	python3 -m pip install $(WHEEL)
	python3 -m cmtg pal.bash flat.clr -
	pip3 freeze
	deactivate

test:
	python3 -m cmtg -h

upload:
	python3 -m twine upload --repository testpypi dist/*

clean:
	$(RM) -r venv
	$(RM) $(WHEEL)
	$(RM) $(SDIST)
