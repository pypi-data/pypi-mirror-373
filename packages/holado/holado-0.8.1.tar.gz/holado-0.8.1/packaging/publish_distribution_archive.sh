#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}/..

if ! python -m pip install --upgrade twine; then
    echo "ERROR: Failed to update 'twine' package"
    exit 1;
fi

VERSION=$(cat "${SCRIPT_DIR}/VERSION")
if ! python -m twine upload --repository pypi ${SCRIPT_DIR}/dist/holado-${VERSION}*; then
    echo "ERROR: Failed to upload HolAdo distribution archives"
    exit 1;
fi
