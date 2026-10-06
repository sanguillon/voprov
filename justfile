default:
    @just --list

# Create/update the virtualenv with all extras and dev dependencies
sync:
    uv sync --all-extras

# Run the test suite
test *args:
    uv run pytest {{args}}

# Run a command with a given prov version, e.g. `just with-prov 2.0.0 pytest`
with-prov version *cmd:
    uv run --with "prov=={{version}}" {{cmd}}

# Build the documentation
docs:
    uv run --group docs sphinx-build docs/source docs/build

# Build sdist and wheel
build:
    uv build

# Remove build artefacts
clean:
    rm -rf build dist *.egg-info docs/build .pytest_cache

# Dump a reference document in all formats to DIR, to compare outputs between versions/branches
dump dir:
    uv run python tests/consistency/build_doc.py {{dir}}
