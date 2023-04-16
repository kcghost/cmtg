.PHONY: all install test-install-wheel test-install-sdist upload clean

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
	python3 -m pip install --force-reinstall $(WHEEL)

test-install-wheel: $(WHEEL)
test-install-sdist: $(SDIST)
test-install-sdist test-install-wheel:
	$(RM) -r venv
	python3 -m venv venv
	source venv/bin/activate
	python3 -m pip install $^
	python3 -m cmtg pal.bash flat.clr -
	python3 -m pip freeze
	deactivate

test:
	python3 -m cmtg -h

# Requires TWINE_USERNAME/TWINE_PASSWORD in environment
upload: $(WHEEL) $(SDIST)
	python3 -m twine check $(WHEEL) $(SDIST)
	#python3 -m twine upload --non-interactive --repository testpypi $(WHEEL) $(SDIST)
	python3 -m twine upload --non-interactive $(WHEEL) $(SDIST)

clean:
	$(RM) -r venv
	$(RM) -r dist/*
