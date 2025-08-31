#!/usr/bin/env python

import os
import sys

IMAGE = 'dunderlab/radiant_p4a.py:latest'
SOURCE = os.path.abspath(os.curdir)
APP = os.path.split(SOURCE)[-1].replace('_', '')

DOCKER_CREATE = f'docker create -i --name {APP} --mount type=bind,source={SOURCE},target=/app/env {IMAGE}'
DOCKER_START = f'docker start {APP}'
DOCKER_EXEC = f'docker exec {APP}'
DOCKER_STOP = f'docker stop {APP}'
# DOCKER_RUN = f'docker run --rm --mount type=bind,source={SOURCE},target=/app/env {IMAGE}'

def main():
    os.system(DOCKER_CREATE)
    os.system(DOCKER_START)
    os.system(f'{DOCKER_EXEC} p4a {" ".join(sys.argv[1:])}')
    os.system(DOCKER_STOP)

if __name__ == '__main__':
    main()