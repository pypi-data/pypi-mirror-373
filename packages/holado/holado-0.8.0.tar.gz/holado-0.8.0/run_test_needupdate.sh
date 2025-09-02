#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

${SCRIPT_DIR}/run_test.sh -i /NonReg -t need_update,ScenarioStatus=NeedUpdate "$@"
