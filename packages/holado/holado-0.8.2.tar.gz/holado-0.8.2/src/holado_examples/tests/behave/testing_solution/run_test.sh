#!/bin/bash

DIR="$(dirname "${BASH_SOURCE[0]}")"
cd ${DIR}

behave --no-source --no-skipped --no-logcapture "$@"

