#!/bin/bash

podman artifact pull $ONNX_ARTIFACT
podman artifact extract $ONNX_ARTIFACT model.onnx

python3 inference/jmp-build-engine.py

podman artifact add quay.io/redhat-et/rhel-bootc-tegra-artifacts:model-plan model.plan
podman artifact push quay.io/redhat-et/rhel-bootc-tegra-artifacts:model-plan
