#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd ${SCRIPT_DIR}/..

if ! pip install --upgrade build; then
    echo "ERROR: Failed to update 'build' package"
    exit 1;
fi

if ! python -m build --outdir ${SCRIPT_DIR}/dist; then
    echo "ERROR: Failed to build HolAdo distribution archive"
    exit 1;
fi
