#!/bin/bash

# set -eux -o pipefail

podman artifact pull $1
podman artifact extract $1 onnx-repository.tar

if [ -f onnx-repository.tar.xz ]; then
	rm onnx-repository.tar.xz
fi

xz onnx-repository.tar

python3 inference/build/jmp-build-engine.py

xz -d plan-repository.tar.xz
podman artifact add $2 plan-repository.tar
podman artifact push $2
