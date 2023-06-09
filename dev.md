# Development

## Host Requirements
```
apt install python3 python3-pip
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
```

## Instant CLI testing
Source `dev.env` to get a `cmtg` function that executes `src/cmtg/cmtg.py`.
It also loads `.env` if existing.
```
. dev.env
cmtg
```

## Build
Build wheel and source distributions:
```
make
```

## Install
Installs the wheel distribution.
A `cmtg` CLI script is made available in `PATH`.
```
make install
```

## Upload to PyPi
* Populate `.env` with credentials
	* `TWINE_USERNAME=__token__`
	* `TWINE_PASSWORD=`, use token generated on PyPI or TestPyPI
* `. .env`
* `make upload`

# todo
* pull from base16
* base16 generator
