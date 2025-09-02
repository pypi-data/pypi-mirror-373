# HolAdo (Holistic Automation do)

# HolAdo

HolAdo, or Holistic Automation do, gives a road to holistic automation in software development.
It's aim is to facilitate many actions by unifying in one framework all needed modules.
Each module delivers a specific need, and it is generally internally using another framework focussed on this need.

HolAdo framework makes it easy to build a solution with many capabilities.
Historically, it was created to easily build powerful functional testing solutions.
But it's conception allows to use it in any context, by integrating only needed HolAdo modules.

In order to improve transparency and maintainability of built solution, 
the Gherkin language is used as a meta-language humanly readable.
Each module includes dedicated steps to easily write scenarios (for testing) or processes (for configuration, deployment,...).


# Status

HolAdo can be used as is, it is stable and maintained.

Until v1.0.0, it is still considered under construction, it is regularly refactored with breaking changes.

To facilitate it's use, each breaking change will result to a new middle version 0.X.0, so that you can update minor versions without problem.


# Python

HolAdo project for Python development.
Python is currently the only one supported language.

Currently, main available modules are:
* ais: manage AIS data
* binary: manipulate binary data, like bit series
* db: manage DB actions (clients, query)
* docker: manage Docker actions
* grpc: manage gRPC clients
* helper: many helpers to easily use HolAdo possibilities (ex: build script/executable using Gherkin language outside of testing context, like to write automatic processes with pseudo code)
* json: manipulate JSON data
* keycloak: a Keycloak client
* logging: add logging capabilities
* multitask: manage multithreading and multiprocessing
* protobuf: manage Protobuf
* python: some tools over python libraries
* rabbitmq: manage RabbitMQ
* redis: manage Redis clients
* report: manage reporting
* rest: manage REST clients
* s3: manage S3 clients
* scripting: add scripting capabilities in other modules
* sftp: manage sFTP clients
* system: manage system actions
* test: core module for testing capability (currently, only BDD tool "behave" is supported)
* value: manage values (like tables with scripting capabilities)
* ws: manage Web Service clients

Major upcomming capabilities:
* WebUI interactions (with playright or selenium)
* DB ORM


# Community

A community around HolAdo is under construction.

For the moment you can contact me by email (eric.klumpp@gmail.com).

For any support, please write scenarios (executable with 'behave') illustating your problem:
* If you encounter a bug, scenarios reproducing the bug.
* If you need an evolution, scenarios illustrating the expected behavior.

If you have implemented a new module, please send it to me, and I will include it in HolAdo framework.

<!-- 

# Howto run HolAdo non-regression tests from docker image got from registry.gitlab.com

Note: Read HolAdo non-regression tests is a good way to discover its capabilities.

* docker login -u XXX registry.gitlab.com
* docker pull registry.gitlab.com/holado_framework/python:main
* docker run --rm -it registry.gitlab.com/holado_framework/python:main /bin/sh -c "cd /code/holado/python; ./run_test_nonreg.sh"

-->

