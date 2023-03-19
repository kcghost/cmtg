.PHONY: all install upload clean

NAME    := $(shell awk -F "=" '/^name/ {gsub(/[ "]/,""); print $$2}' pyproject.toml)
VERSION := $(shell awk -F "=" '/^version/ {gsub(/[ "]/,""); print $$2}' pyproject.toml)
SRC     := $(shell find src/ -type f) pyproject.toml
WHEEL   := dist/$(NAME)-$(VERSION)-py3-none-any.whl
SDIST   := dist/$(NAME)-$(VERSION).tar.gz

all: $(WHEEL) $(SDIST)

$(WHEEL): $(SRC)
	python3 -m build -w

$(SDIST): $(SRC)
	python3 -m build -s

install: $(WHEEL)
	pip3 install --force-reinstall $(WHEEL)

upload:
	python3 -m twine upload --repository testpypi dist/*

clean:
