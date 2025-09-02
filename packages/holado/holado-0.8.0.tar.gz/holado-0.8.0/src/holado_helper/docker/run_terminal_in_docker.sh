#!/bin/bash

# Script to launch a command with testing docker.
#
# It is usually used to launch a script embedded in docker image.
#
# USAGE:
#     Considering a working directory WORK_DIR, to launch scenarios, open a console in WORK_DIR, and launch the script with wanted parameters (see bellow).
#
#     Example: display feature & scenario durations of a report
#              run_terminal_in_docker.sh python ./resources/scripts/print_report_execution_historic.py -r {dirname_to_report} -f feature.name -f feature.filename -f feature.duration -s scenario.name -s scenario.line -s scenario.duration
#
# REQUIREMENTS:
#     Define in .profile the following variables
#         - HOLADO_IMAGE_TAG: docker image tag to use (usually "main" or tag associated to any branch)
#         - optional but preferable:
#             - HOLADO_OUTPUT_BASEDIR: absolute path to base output directory of testing solution
#             - HOLADO_LOCAL_RESOURCES_BASEDIR: absolute path to base local resources directory of testing solution (where data are stored through campaigns)
#         - optional:
#             - HOLADO_USE_LOCALHOST: force the container network to 'host'.
#             - HOLADO_NETWORK: specify on which network the docker is run.
#     Example:
#         export HOLADO_IMAGE_TAG=main
#         export HOLADO_USE_LOCALHOST=True
#         export HOLADO_OUTPUT_BASEDIR=$HOME/.holado/output
#         export HOLADO_LOCAL_RESOURCES_BASEDIR=$HOME/.holado/resources
#


for v in HOLADO_IMAGE_TAG; do
    if [ -z ${!v} ]; then
        echo "Environment variable $v must be set"
        exit 1
    fi
done

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
	NETWORK_DEF_COMMAND="--network=host"
else
	if [[ ! -z "$HOLADO_NETWORK" ]]; then
		NETWORK_DEF_COMMAND="--network $HOLADO_NETWORK"
	else
		NETWORK_DEF_COMMAND=""
	fi
fi

# Docker run 
if [[ -z "$HOLADO_RUNNER_NAME" ]]; then
    HOLADO_RUNNER_NAME=holado_test_runner
fi

echo
echo "Running tests (docker name: ${HOLADO_RUNNER_NAME})..."
echo
docker run --rm -it $(docker info | grep -i rootless > /dev/null && echo -n "--user root" || echo -n "-u $(id -u ${USER}):$(id -g ${USER})") --name ${HOLADO_RUNNER_NAME} \
    -v "${OUTPUT_DIR}":/output \
    -v "${RESOURCES_DIR}":/resources \
    -e HOLADO_OUTPUT_BASEDIR=/output \
    -e HOLADO_LOCAL_RESOURCES_BASEDIR=/resources \
    ${NETWORK_DEF_COMMAND} \
    -w /work_dir \
    ${TEST_IMAGE} /bin/bash

