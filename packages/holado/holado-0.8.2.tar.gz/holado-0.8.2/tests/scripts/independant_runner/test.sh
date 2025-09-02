#!/bin/bash

CWD="$(dirname "${BASH_SOURCE[0]}")"

python3 "${CWD}"/test.py "$@"

#read -p "Press [Enter] key to finish..."
