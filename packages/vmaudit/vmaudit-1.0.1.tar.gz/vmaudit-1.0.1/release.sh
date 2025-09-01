#!/usr/bin/env bash

set -e

# Ensure that we are in the correct directory.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

cd -- "${SCRIPT_DIR}"

# Create build environment.
_build_env="${SCRIPT_DIR}/.venv-build"

_first_install="false"
if [[ ! -e "${_build_env}" ]]; then
    echo -e "\nCreating environment..."
    python3 -m venv "${_build_env}"
    _first_install="true"
fi

source "${_build_env}/bin/activate"

if [[ "${_first_install}" == "true" ]]; then
    echo -e "\nInstalling dependencies..."
    python3 -m pip install --upgrade pip
    python3 -m pip install --upgrade build twine
fi

# Build fresh packages.
# SEE: https://packaging.python.org/en/latest/tutorials/packaging-projects/
rm -rf dist

echo -e "\nBuilding packages..."
python3 -m build

# Upload to PyPI.
# SEE: https://packaging.python.org/en/latest/specifications/pypirc/
if [[ "${1:-}" == "upload" ]]; then
    echo -e "\nUploading packages..."
    python3 -m twine upload dist/*
fi

deactivate
