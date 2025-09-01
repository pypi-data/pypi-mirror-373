# klaatu-python

A bunch of more or less useful Python utils without any 3rd party dependencies.

## Development install

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Inclusion in projects

In `pyproject.toml`:
```
[project]
dependencies = [
    "klaatu-python",
    ...
]
```
