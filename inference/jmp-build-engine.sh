#!/bin/bash

podman artifact pull $1
podman artifact extract $1 model.onnx

python3 inference/jmp-build-engine.py

podman artifact add $2 model.plan
podman artifact push $2
