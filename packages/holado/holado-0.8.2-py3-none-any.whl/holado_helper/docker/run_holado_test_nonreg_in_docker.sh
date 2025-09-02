#!/bin/bash

# Script to launch run_test.sh with testing docker.
#
# This script helper is written to run HolAdo tests.
# With this script, the features to launch are embedded in docker image.
#
# USAGE:
#     Considering a working directory WORK_DIR, to launch scenarios, open a console in WORK_DIR, and launch the script with wanted parameters (see bellow).
#     Then a new report is added in folder HOLADO_OUTPUT_BASEDIR/reports if environment variable HOLADO_OUTPUT_BASEDIR is defined, else in folder WORK_DIR/reports.
#
# REQUIREMENTS:
#     Define in .profile the following variables
#         - HOLADO_IMAGE_TAG: docker image tag to use (usually "main" or tag associated to any branch)
#         - optional but preferable:
#             - HOLADO_OUTPUT_BASEDIR: absolute path to base output directory of testing solution
#             - HOLADO_LOCAL_RESOURCES_BASEDIR: absolute path to base local resources directory of testing solution (where data are stored through campaigns)
#         - optional:
#             - HOLADO_IMAGE_REGISTRY: docker image registry to use (default: "registry.gitlab.com/holado_framework/python")
#             - HOLADO_USE_LOCALHOST: force the container network to 'host'.
#             - HOLADO_NETWORK: specify on which network the docker is run.
#     Example:
#         export HOLADO_IMAGE_TAG=main
#         export HOLADO_USE_LOCALHOST=True
#         export HOLADO_OUTPUT_BASEDIR=$HOME/.holado/output
#         export HOLADO_LOCAL_RESOURCES_BASEDIR=$HOME/.holado/resources
#
# If no parameters are added to the script, all features/scenarios are run.
# Additional parameters can be specified to change runner behaviors, usually used to execute specific features/scenarios.
# In order to execute specific scenarios, the easiest way is to filter scenarios by tags with "-t" parameter.
# For example, following command executes all scenarios having both tags "scenario" and "table_possible_values": 
#      run_test_in_docker.sh -t scenario -t table_possible_values
#
# Note: Technically, the additional parameters are directly passed to internal script run_test.sh. 
#       For a complete help on possible parameters, simply add "-h" to command. 


for v in HOLADO_IMAGE_TAG; do
    if [ -z ${!v} ]; then
        echo "Environment variable $v must be set"
        exit 1
    fi
done

CWD="$(dirname "${BASH_SOURCE[0]}")"
WORK_DIR="$(pwd)"

if [[ -z "$HOLADO_IMAGE_REGISTRY" ]]; then
    HOLADO_IMAGE_REGISTRY=registry.gitlab.com/holado_framework/python
fi
TEST_IMAGE=${HOLADO_IMAGE_REGISTRY}:${HOLADO_IMAGE_TAG}

# Update docker image
echo "Updating docker image ${TEST_IMAGE}..."
docker pull ${TEST_IMAGE}

# Define test output directory
if [[ ! -z "$HOLADO_OUTPUT_BASEDIR" ]]; then
    OUTPUT_DIR=${HOLADO_OUTPUT_BASEDIR}
else
    OUTPUT_DIR=${WORK_DIR}/output
fi
echo "Output directory: $OUTPUT_DIR"

# Define test resources directory
if [[ ! -z "$HOLADO_LOCAL_RESOURCES_BASEDIR" ]]; then
    RESOURCES_DIR=${HOLADO_LOCAL_RESOURCES_BASEDIR}
else
    RESOURCES_DIR=${WORK_DIR}/resources
fi
echo "Resources directory: $RESOURCES_DIR"

# Make dirs
if [ ! -d ${OUTPUT_DIR} ]; then
    echo "Create output directory: ${OUTPUT_DIR}"
    mkdir -p ${OUTPUT_DIR}
fi
if [ ! -d ${RESOURCES_DIR} ]; then
    echo "Create resources directory: ${RESOURCES_DIR}"
    mkdir -p ${RESOURCES_DIR}
fi

# Define container network
if [ "$HOLADO_USE_LOCALHOST" = True ]; then
    NETWORK_DEF_CMD="--network=host"
else
    if [[ ! -z "$HOLADO_NETWORK" ]]; then
        NETWORK_DEF_CMD="--network $HOLADO_NETWORK"
    else
        NETWORK_DEF_CMD=""
    fi
fi

# Define if logging.conf must be override
if [ -f ${WORK_DIR}/logging.conf ]; then
    LOGGING_CONF_CMD="-v ${WORK_DIR}/logging.conf:/code/holado/python/tests/behave/test_holado/logging.conf"
elif [ -f ${CWD}/logging.conf ]; then
    LOGGING_CONF_CMD="-v ${CWD}/logging.conf:/code/holado/python/tests/behave/test_holado/logging.conf"
else
    LOGGING_CONF_CMD=""
fi

# Docker run 
if [[ -z "$HOLADO_RUNNER_NAME" ]]; then
    HOLADO_RUNNER_NAME=holado_test_runner
fi

echo
echo "Running tests (docker name: ${HOLADO_RUNNER_NAME})..."
echo
# Note: In bellow command, some non-regression scenarios are skipped, those currently not working when run in docker
docker run --rm -t $(docker info | grep -i rootless > /dev/null && echo -n "--user root" || echo -n "-u $(id -u ${USER}):$(id -g ${USER})") --name ${HOLADO_RUNNER_NAME} \
	-v "${OUTPUT_DIR}":/output \
	-v "${RESOURCES_DIR}":/resources \
	${LOGGING_CONF_CMD} \
    -e HOLADO_OUTPUT_BASEDIR=/output \
    -e HOLADO_LOCAL_RESOURCES_BASEDIR=/resources \
	${NETWORK_DEF_CMD} \
	${TEST_IMAGE} /bin/bash -c "./run_test_nonreg.sh -t ~grpc -t ~rabbitmq -t ~sftp $*"

