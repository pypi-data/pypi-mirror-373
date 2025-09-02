/!\ UNDER CONSTRUCTION

==============
HolAdo (Holistic Automation do)
==============

Framework dedicated to facilitate automation, including functional testing automation.


Howto run tests from docker image got from registry.gitlab.com
==============

- docker login -u XXX registry.gitlab.com
- docker pull registry.gitlab.com/holado_framework/python:main
- docker run --rm -it registry.gitlab.com/holado_framework/python:main /bin/sh -c "cd /code/holado/python; ./run_test.sh"


Howto create a gitlab runner
==============

1. Setup OS.   
Example as a VM:  
- Create a VM with last ubuntu
- Update repo: 
  sudo apt update
- update system:  
  sudo apt full-upgrade

2.  Install dev tools: 
  sudo apt install build-essential

3.  Follow this howto:   
<https://www.balticlsc.eu/gitlab/help/ci/docker/using_docker_build.md>
  
Known working installation:
- Install gitlab-runner by deb package: download last 'deb/gitlab-runner_amd64.deb', and install "dpkg -i gitlab-runner_amd64.deb"
- Install docker by distribution packages. Example: on ubuntu 20.04, install 'docker' and 'docker-io'


