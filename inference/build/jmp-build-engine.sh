#!/bin/bash

set -x

podman artifact pull $1
podman artifact extract $1 onnx-repository.tar.xz

python3 inference/build/jmp-build-engine.py

podman artifact add $2 plan-repository.tar.xz
podman artifact push $2
