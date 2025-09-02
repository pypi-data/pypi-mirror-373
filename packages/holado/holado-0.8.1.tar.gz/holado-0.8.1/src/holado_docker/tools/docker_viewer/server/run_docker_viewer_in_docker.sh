#!/bin/bash

# Script to launch Docker Viewer as a docker image.
# 
# Docker Viewer exposes a REST API for some docker commands.
# It is accessible on localhost, and also on a docker network if HOLADO_NETWORK is defined.
# On all networks, API is accessible on same port (HOLADO_DOCKER_VIEWER_PORT or 8000).
#
# REST API specification is in file rest/openapi.yaml.
#
# REQUIREMENTS:
#     Have access to any HolAdo registry.
#
#     Optionally, define in .profile the following variables
#         - HOLADO_DOCKER_VIEWER_PORT: REST API port to use (default: 8000)
#         - HOLADO_IMAGE_REGISTRY: docker image registry to use (default: holado/docker_viewer)
#         - HOLADO_IMAGE_TAG: docker image tag to use (default: latest)
#         - HOLADO_OUTPUT_BASEDIR: absolute path to base output directory (default: [HOME]/.holado/output)
#         - HOLADO_USE_LOCALHOST: force the container network to 'host'.
#         - HOLADO_NETWORK: specify on which network the docker is run.
#


WORK_DIR="$(pwd)"

if [[ -z "$HOLADO_IMAGE_REGISTRY" ]]; then
    HOLADO_IMAGE_REGISTRY=holado/docker_viewer
fi
if [[ -z "$HOLADO_IMAGE_TAG" ]]; then
    HOLADO_IMAGE_TAG=latest
fi
VIEWER_IMAGE=${HOLADO_IMAGE_REGISTRY}:${HOLADO_IMAGE_TAG}

# Update docker image
echo "Updating docker image ${VIEWER_IMAGE}..."
docker pull ${VIEWER_IMAGE}

# Define test output directory
if [[ ! -z "$HOLADO_OUTPUT_BASEDIR" ]]; then
    OUTPUT_DIR=${HOLADO_OUTPUT_BASEDIR}
else
    OUTPUT_DIR=${HOME}/.holado/output
fi
echo "Output directory: $OUTPUT_DIR"

# Define test resources directory
if [[ ! -z "$HOLADO_LOCAL_RESOURCES_BASEDIR" ]]; then
    RESOURCES_DIR=${HOLADO_LOCAL_RESOURCES_BASEDIR}
else
    RESOURCES_DIR=${HOME}/.holado/resources
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

# Define port to use
if [[ -z "$HOLADO_DOCKER_VIEWER_PORT" ]]; then
    HOLADO_DOCKER_VIEWER_PORT=8000
fi


# Docker run 
if [[ -z "$HOLADO_DOCKER_VIEWER_NAME" ]]; then
    HOLADO_DOCKER_VIEWER_NAME=holado_docker_VIEWER
fi

echo
echo "Running Docker VIEWER (docker name: ${HOLADO_DOCKER_VIEWER_NAME})..."
echo "    port: ${HOLADO_DOCKER_VIEWER_PORT}"
#echo "    NETWORK_DEF_COMMAND=${NETWORK_DEF_COMMAND}"
echo
docker run --rm --user root --name ${HOLADO_DOCKER_VIEWER_NAME} \
    --privileged -v /var/run/docker.sock:/var/run/docker.sock \
    -v "${OUTPUT_DIR}":/output \
    -v "${RESOURCES_DIR}":/resources \
    -e HOLADO_OUTPUT_BASEDIR=/output \
    -e HOLADO_LOCAL_RESOURCES_BASEDIR=/resources \
    -e HOLADO_DOCKER_VIEWER_PORT=${HOLADO_DOCKER_VIEWER_PORT} \
    ${NETWORK_DEF_COMMAND} \
    -p ${HOLADO_DOCKER_VIEWER_PORT}:${HOLADO_DOCKER_VIEWER_PORT} \
    ${VIEWER_IMAGE}

