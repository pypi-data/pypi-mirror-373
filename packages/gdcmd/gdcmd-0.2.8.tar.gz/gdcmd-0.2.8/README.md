# Griddot python package

A place for all common python code

## Python terminology

- package: A collection of modules, classes, and functions that are organized in a directory hierarchy, with an `__init__.py` file at the top level.
- package: A collection of modules that is normally published to PyPI and can be installed using pip.
- module: A single file containing Python code, which can be imported into other modules or scripts.
- script: A Python file that is intended to be run directly (not just imported).
- namespace: A package without an `__init__.py` file, used when splitting one logical package across multiple directories or distributions (rare in small projects).

## Development

Run `gdcmd` in development with: `uv sync; uv run gdcmd`.
Running tests: `uv run pytest --ignore=tests/manual -v tests`.
Testing `gdcmd` from inside container locally:

```shell
# First time
uv build; podman run -d --name gdcmd --replace -v ./dist:/dist python:3.12-slim bash -lc "pip install /dist/*.whl && sleep infinity"

# Run
podman exec -it gdcmd gdcmd --help

# Rebuild
uv build; podman exec -it gdcmd bash -lc "pip install /dist/*.whl --force-reinstall"

# Deployment testing
cd python; uv build; cd ../charts/suite; helm template . --set common.reseller=local --set common.tenant=test -f values.yaml | podman kube play --replace --network suite - ; cd ../..
```