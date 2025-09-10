# Edge AI Image Pipelines

This repository contains several workflows to automate the building and testing of inference stacks on the edge.

These pipelines are triggered with a simple `workflow_dispatch` event, but must be configured for your usecase first.

The result of this pipeline will be a number of tags in your configured `DEST_REGISTRY_REPO` containing both Bootc container images and `.raw.xz` compressed Bootc disk images flashable to an NVIDIA Jetson device.

The tags are:
* `base`: a base image containing the necessary JetPack drivers to run AI workflows
* `ollama`: ollama Server
* `vllm`: vLLM Server
* `triton`: Triton Inference Server
* `triton-microshift`: Triton Inference Server on Microshift

For each tag TAG, `${TAG}-raw` will also be generated with the flashable Bootc image

## Table of Contents

[Quick Start](#quick-start)

Configuring image build:
* [Global Configuration](#variables-required)
* [Ollama](#ollama-build-config)
* [vLLM](#vllm-build-config)
* [Triton](#triton-build-config)
* [Microshift](#microshift-build-config)

Running images:
* [Integration Tests](#integration-tests)
* [Ollama](#running-ollama)
* [vLLM](#running-vllm)
* [Triton](#running-triton)
* [Triton Microshift](#running-triton-microshift)

Building Custom Images:
* [How To](#building-custom-images)

Troubleshooting:
* [Jumpstarter gRPC Timeouts](#grpc-troubleshooting)

## Configuration

### Quick Start

A number of pre-built RHEL Bootc Jetson images are available on [Quay](https://quay.io/repository/redhat-et/rhel-bootc-tegra?tab=tags&tag=latest) as OCI artifacts. Each `$APP-raw` tag is an xz-compressed Bootc image of the corresponding app. To run one of these applications, flash the image to your Jetson device and consult the corresponding section in [Running Images](#running-images).

If you'd like to build your own Bootc Images (e.g. with different models or extra services):
* Configure repository variables and secrets according to [Section: Variables](#variables-required). Note that if you aren't building Triton or Microshift, there are certain variables you do not have to configure.
* Consult the corresponding section under "Configuring image build" OR if you need more advanced configuration consult [Building Custom Images](#building-custom-image)
* Run the corresponding workflow. This will take a while

### Variables (Required)

In order to use these pipelines, a number of GitHub Repository secrets and variables must be configured.

The secrets configure authentication with three different container registries, the `SOURCE` registry contains the base RHEL Bootc image (registry.redhat.io), an `ARTIFACTS` registry where consumable, non-final artifacts are stored, and a `DEST` registry where the compiled images are stored

Required Repository Secrets:
* `ARTIFACT_REGISTRY_PASSWORD`
* `ARTIFACT_REGISTRY_USER`
* `DEST_REGISTRY_PASSWORD`
* `DEST_REGISTRY_USER`
* `SOURCE_REGISTRY_PASSWORD`
* `SOURCE_REGISTRY_USER`
* `RHT_ACT_KEY`: A Red Hat subscription manager activation key
* `RHT_ORGID`: A Red Hat subscription manager organization ID
* `JUMPSTARTER_CLIENT_CONFIG`: A Jumpstarter user config YAML document (only required for running Triton Server build and integration tests)
* `OPENSHIFT_PULL_SECRET`: An OpenShift pull secret obtained from Red Hat Cluster Mananger (only required for running Microshift build)

Required Repository Variables:
* `ARTIFACT_REGISTRY_HOST`
* `ARTIFACT_REGISTRY_REPO`
* `DEST_REGISTRY_HOST`
* `DEST_REGISTRY_REPO`
* `JUMPSTARTER_SELECTOR`: Jumpstarter selector used to acquire Jumpstarter-controlled device for these workflows (passed as `jmp create lease --selector $JUMPSTARTER_SELECTOR`)

### Ollama Build Config

You can configure models installed by "Build Ollama Server" `workflow_dispatch` by simply listing the models from the [Ollama Library](https://ollama.com/library) (space delimited) in the `models` input

### vLLM Build Config

You can configure models installed by "Build vLLM Server" `workflow_dispatch` by simply listing the set of HuggingFace repositories (space delimited) in the `models` input.

### Triton Build Config

Triton server uses the highly performant `.plan` format for models. These are acquired by natively (on-device) compiling them from `.onnx` using `trtexec`. To set up your models for compilation, do the following:
* Export models to `.onnx` format
* Create a directory `onnx-repository`
* Move each model to `onnx-repository/<model name>/<version>/model.onnx`
* Tar `onnx-repository`
* Push `onnx-repository.tar` to your artifact registry with the tag onnx-repository

As an example:

```
mkdir onnx-repository
mkdir -p onnx-repository/ram_plus/1
mv ram_plus.onnx onnx-repository/ram_plus/1/model.onnx
mkdir -p onnx-repository/yolo11x/1
mv yolo11x.onnx onnx-repository/yolo11x/1/model.onnx

tar cf onnx-repository.tar onnx-repository

ref=$ARTIFACT_REGISTRY_HOST/$ARTIFACT_REGISTRY_REPO:onnx-repository
podman artifact add $ref onnx-repository.tar
podman artifact push $ref
```

When `build-triton.yml` is run it will compile these models into .plan format using the pipeline's jumpstarter device and reupload it to `ARTIFACT_REGISTRY_REPO` under the tag `plan-repository`. This is subsequently consumed by the pipeline to produce your Bootc image.

### MicroShift Setup

If you'd like to deploy application containers (e.g. Triton Inference Server, vLLM) on MicroShift, use the "Add MicroShift to Bootc Image" workflow. It will install MicroShift along with the resources required to give your MicroShift pods access to the iGPU.

The `workflow_dispatch` event has the following inputs:
* `resource_definitions`: a space-delimited list of resources to apply as Kustomizations. These can either be Web URLs or paths within this repository given relative to the `/repo` mount. (e.g. `./triton/microshift/triton.yml` would be given as `/repo/triton/build/triton.yml`)
* `input_image`: A reference to the Bootc container image that MicroShift should be added to
* `tags_list`: Tag list to apply to the output image

An example resource definition for a Triton Inference Server can be found in `./triton/microshift/triton.yml`.

The flashable bootc image will be pushed to `$DEST_REGISTRY_HOST/$DEST_REGISTRY_REPO:$tag` for each tag in `tags_list`

## Running Images

### Integration Tests

Integration testing is done via `jumpstarter` as found in `./.github/workflows/run-jumpstarter-workflow.yml`. To run integration tests, you can use this action to flash your produced image onto your Jetson device and run tests using the Jumpstarter Python API.

The workflow takes the following inputs:
* `image-url`: Reference to the image you'd like to test (e.g. `${{ vars.DEST_REGISTRY_HOST }}/${{ vars.DEST_REGISTRY_REPO }}:vllm-raw`)
* `jumpstarter-selector`: Selector used to identify the Jumpstarter device to test (will be passed to jmp as `jmp create lease --selector ${{ inputs.jumpstarter-selector }}`)
* `workflow-cmd`: Command to run under Jumpstarter lease. Generally, this will call a Python script (e.g. `./triton/tests/test_triton.py`) that will do all the heavy lifting.

A number of example workflows are found in this repository as `./.github/workflows/test-*`.

### Running Ollama

Tag: `ollama-raw`

Run `podman run --device nvidia.com/gpu=all --ipc=host ${ARTIFACT_REGISTRY_HOST}/${ARTIFACT_REGISTRY_REPO}:ollama-worker ollama serve`. If using the prebuilt image from quay.io/redhat-et, `${ARTIFACT_REGISTRY_HOST}/${ARTIFACT_REGISTRY_REPO}` is `quay.io/redhat-et/rhel-bootc-tegra-artifacts`.

### Running vLLM

Tag: `vllm-raw`

Run `podman run --name server --network vllm -d --device nvidia.com/gpu=all --ipc=host -p8000:8000 -v .:/share -v /usr/share/huggingface:/huggingface quay.io/redhat-user-workloads/octo-edge-tenant/jetson-wheels-vllm-app:latest /bin/bash -c \"/app/bin/python -m vllm.entrypoints.openai.api_server --model /huggingface/<your model> --gpu_memory_utilization=0.8 --max_model_len=6000 > /share/vllm.log\"` where `<your model>` is one of the configured huggingface repos from [vLLM build](#vllm-server-setup). If using the prebuilt image from quay.io/redhat-et, the only model available will be ibm-granite/granite-vision-3.2-2b

If you're curious, here's a breakdown of the command-line options used in this one-liner:
* `-p8000:8000`: Exposes the vLLM OpenAI API server to the host
* `-v .:/share`: Mounts the CWD as a volume for vLLM so we can collect logs
* `-v /usr/share/huggingface:/huggingface`: Mounts the hugginface diretory as a volume for vLLM
* `--device nvidia.com/gpu=all`: Makes CUDA system and other gpu-related resources available to vLLM using NVIDIA CDI
* `--gpu_memory_utilization=0.8`: Since this is a Jetson, the GPU is an iGPU and memory is shared with the CPU, so 100% of the memory will never be available for vLLM, and vLLM will fail if it cannot achieve the configured memory utilization. This defaults to 1.0, so we must set it lower
* `--max_model_len=6000`: Since we are likely resource-constrained, set maximum context length to something (relatively) small to prevent us from going OOM

### Running Triton

Tag: `triton-raw`

Run `podman run --rm -d --device nvidia.com/gpu=all --ipc=host -p8000:8000 -p8001:8001 -p8002:8002 -v /models:/models nvcr.io/nvidia/tritonserver:25.07-py3-igpu tritonserver --model-repository=/models`. The Triton Inference Server is now available on localhost and can be accessed using the Triton client libraries (example given in ./triton/tests/triton-client.py).

## Building Custom Images

The CI for each image can be customized easily to with additional application containers or models. To do this, see the corresponding section in [configuration](#configuration). If you would like to do something more sophisticated (e.g. installing systemd units), then you will most likely need to create a new GitHub Actions job that adds these features before its compiled to a disk image. To do so:
* Create a Containerfile `$CONTAINERFILE` somewhere in this GitHub containing the modification to one of the already existing Bootc images
* Create a workflow in `.github/workflows/` that uses [build-rhel-bootc-image.yml](.github/workflows/build-rhel-bootc-image.yml) with $CONTAINERFILE as the configured containerfile
* Add a call to [build-rhel-bootc-raw-image.yml](.github/workflows/build-rhel-bootc-raw-image.yml) to create the disk image
* Invoke the workflow with a `workflow_dispatch` event. This will probably take a while.

For an example of how to do this, see `.github/workflows/build-ollama.yml`

## Troubleshooting

### Troubleshooting gRPC

We highly recommend setting `grpcOptions["grpc.keepalive_time_ms"]` and `grpcOptions["grpc.keepalive_timeout_ms"]` in your `JUMPSTARTER_CLIENT_CONFIG` to something safe (e.g. 10000 ms) if you start experiencing gRPC timeouts during the various Jumpstarter workflows in this repository.
