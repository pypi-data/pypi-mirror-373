#!/bin/bash

DIR="$(dirname "${BASH_SOURCE[0]}")"

${DIR}/run_test.sh -i NonReg -t ~draft -t ~need_update -t ~ScenarioStatus=Draft -t ~ScenarioStatus=NeedUpdate "$@"

