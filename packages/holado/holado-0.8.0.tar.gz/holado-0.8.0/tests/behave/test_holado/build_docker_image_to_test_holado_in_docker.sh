#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"/../../..

docker build . -t test_holado -f tests/behave/test_holado/Dockerfile_test_holado


