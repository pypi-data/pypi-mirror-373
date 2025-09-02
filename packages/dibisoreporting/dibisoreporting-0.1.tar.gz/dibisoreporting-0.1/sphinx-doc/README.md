# Build the documentation

Commands to be run from this directory (`sphinx-doc/`).

## Load the virtual environment

```bash
source ../.venv/bin/activate
```

## Install the dependencies

```bash
pip install -r requirements.txt
```

Make sure Pandoc is installed (Ubuntu: `sudo apt install pandoc`).

## Build the documentation

```bash
make html
```

You can use `make clean` to remove previous build files.


Romain THOMAS 2025
Licence: AGPLv3
