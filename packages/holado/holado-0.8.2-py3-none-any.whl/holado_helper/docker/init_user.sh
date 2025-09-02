#!/bin/bash

# Script to init a new docker user as existing user appuser.
#
# Default HolAdo Dockerfile creates a user appuser, configure it so that it can run tests, and it runs as this user.
# When defining a specific new user when running docker image, this user is not configured to be able to run tests.
# The purpose of this script is to give a simple solution to initialize this new user as user appuser.
#
# USAGE:
#     In the command run in docker, call this script before the command to execute.
#
#     Example: to run all non-reg tests as a specific user defined in run command, set in yaml file
#
#           user: ${TEST_UID}:${TEST_GID}
#           command: "bash -c \"/code/holado/python/src/holado_helper/docker/init_user.sh && ./run_test_nonreg.sh\""


# Activate python venv
source /code/env/bin/activate

# Set environment variables needed by HolAdo
export HOLADO_PATH=/code/holado/python/


