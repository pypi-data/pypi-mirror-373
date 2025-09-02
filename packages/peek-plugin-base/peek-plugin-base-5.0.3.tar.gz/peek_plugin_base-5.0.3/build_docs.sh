#!/usr/bin/env bash
PACKAGE="peek_plugin_base"

set -o nounset # Error on unset variables
set -o errexit # Exit if a command fails

echo "Retrieving latest version tag"
VER=$(git describe --tags $(git rev-list --tags --max-count=1))

echo "Setting version to $VER"
sed -i "s;.*version.*;__version__ = '${VER}';" ${PACKAGE}/__init__.py

echo "==========================================="
echo "Building Sphinx documentation for '${PACKAGE}'!"
echo "==========================================="

echo "Removing old documentation in build folder..."
rm -fr dist/docs/*

echo "Creating Python Path"
export PYTHONPATH="$(pwd)"

echo "Ensure Sphinx and the theme that Synerty uses is installed..."
for pkg in Sphinx sphinx-rtd-theme; do
    if ! pip freeze | grep -q "${pkg}=="; then
        echo "Installing ${pkg}"
        pip install ${pkg}
    fi
done

echo "Running Sphinx-apidoc"
sphinx-apidoc -f -l -d 6 -o docs . '*Test.py' 'setup.py'

sphinx-build -b html docs dist/docs

echo "Removing old module rst files..."
rm -fr docs/peek* docs/modules.rst

echo "Opening created documentation..."
start dist/docs/index.html
