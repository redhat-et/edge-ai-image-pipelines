# Edge Pipelines for Model Validation

This repository contains several workflows to automate the building, testing, and releasing of inference stacks on the edge.

These pipelines are triggered with a simple `workflow_dispatch` event, but must be configured for your usecase first.

The result of this pipeline will be a number of tags in your configured `DEST_REGISTRY_REPO` containing both Bootc container images and `.raw.xz` compressed Bootc disk images flashable to an NVIDIA Jetson device.

The tags are:
* `base`: a base image containing the necessary JetPack drivers to run AI workflows
* `ollama`: ollama Server
* `vllm`: vLLM Server
* `triton`: Triton Server
* `triton-microshift`: Triton Server

For each tag TAG, `${TAG}-raw` will also be generated with the flashable Bootc image

## Table of Contents

To configure each of the application build pipelines:
* [Global Configuration](#variables-required)
* [Ollama](#ollama-setup)
* [Triton](#triton-setup)
* [vLLM](#vllm-setup)

To set up integration tests:

## Configuration

### Variables (Required)

In order to use these pipelines, a number of GitHub Repository secrets and variables must be configured.

The secrets configure authentication with three different container registries, the `SOURCE` registry contains the base RHEL Bootc image (registry.redhat.io), an `ARTIFACTS` registry where consumable artifacts are stored, and a `DEST` registry where the compiled images are stored

Required Repository Secrets:
* `ARTIFACT_REGISTRY_PASSWORD`
* `ARTIFACT_REGISTRY_USER`
* `DEST_REGISTRY_PASSWORD`
* `DEST_REGISTRY_USER`
* `SOURCE_REGISTRY_PASSWORD`
* `SOURCE_REGISTRY_USER`
* `RHT_ACT_KEY`: A Red Hat subscription manager activation key
* `RHT_ORGID`: A Red Hat subscription manager organization ID
* `JUMPSTARTER_CLIENT_CONFIG`: A Jumpstarter user config YAML document
* `OPENSHIFT_PULL_SECRET`: An OpenShift pull secret (obtained from Red Hat Cluster Mananger)

Required Repository Variables:
* `ARTIFACT_REGISTRY_HOST`
* `ARTIFACT_REGISTRY_REPO`
* `DEST_REGISTRY_HOST`
* `DEST_REGISTRY_REPO`
* `JUMPSTARTER_SELECTOR`: Jumpstarter selector used to acquire Jumpstarter-controlled device for these workflows (passed as jmp create lease --selector $JUMPSTARTER_SELECTOR)

### Ollama Setup

To configure Ollama with a particular model, simply add it's name from the Ollama Library to MODELS in `./.github/workflows/build-ollama.yml`

### Triton Inference Server Setup

In order to run Triton Inference Server, you first need models. To achieve maximum performance, models must be compiled to the `.plan` format using `trtexec` on-device. To prepare your models to be run on Triton, first convert them to the ONNX format, place them in a `onnx-repository` directory, each at the path `onnx-repository/{model name}/{version}/model.onnx`, and then TAR this directory and upload it to your `ARTIFACT_REGISTY_REPO` with tag `onnx-repository`, e.g.

```
ref=$ARTIFACT_REGISTRY_HOST/$ARTIFACT_REGISTRY_REPO:onnx-repository

mkdir onnx-repository
mkdir -p onnx-repository/ram_plus/1
mv ram_plus.onnx onnx-repository/ram_plus/1/model.onnx
mkdir -p onnx-repository/yolo11x/1
mv yolo11x.onnx onnx-repository/yolo11x/1/model.onnx

tar cf onnx-repository.tar onnx-repository
podman artifact add $ref onnx-repository.tar
podman artifact push $ref
```

The pipeline will then automatically compile these models into .plan format using the pipeline's jumpstarter device and reupload it to `ARTIFACT_REGISTRY_REPO` under the tag `plan-repository`. This is subsequently consumed by the pipeline to produce your Bootc image.

### vLLM Server Setup

vLLM models are stored in HuggingFace repositories. To add your models to the vLLM image you can modify the `HF_REPOS` build variable found in `./.github/workflows/build-vllm.yml`.

Additionally, you must use custom wheels for both PyTorch and vLLM. While we currently have no official CI that serves these, they are currently pulled from `quay.io/ncao/wheels`. They will be installed to the venv found at `/app`.


### MicroShift Setup

If you'd like to deploy application containers (e.g. Triton Inference Server, vLLM) on MicroShift, use the "Add MicroShift to Bootc Image" workflow. It will install MicroShift along with the resources required to give your MicroShift pods access to the iGPU.

The `workflow_dispatch` event has the following inputs:
* `resource_definitions`: a space-delimited list of resources to apply as Kustomizations. These can either be Web URLs or paths within this repository given relative to the `/repo` mount. (e.g. `./triton/microshift/triton.yml` would be given as `/repo/triton/build/triton.yml`)
* `input_image`: A reference to the Bootc container image that MicroShift should be added to
* `tags_list`: Tag list to apply to the output image

The flashable bootc image will be pushed to `$DEST_REGISTRY_HOST/$DEST_REGISTRY_REPO:$tag` for each tag in `tags_list`


## Integration Testing

Integration testing is done via `jumpstarter` as found in `./.github/workflows/run-jumpstarter-workflow.yml`. To run integration tests, you can use this action to flash your produced image onto your Jetson device and run tests using the Jumpstarter Python API.

The workflow takes the following inputs:
* `image-url`: Reference to the image you'd like to test (e.g. `${{ vars.DEST_REGISTRY_HOST }}/${{ vars.DEST_REGISTRY_REPO }}:vllm-raw`)
* `jumpstarter-selector`: Selector used to identify the Jumpstarter device to test (will be passed to jmp as `jmp create lease --selector ${{ inputs.jumpstarter-selector }}`)
* `workflow-cmd`: Command to run under Jumpstarter lease. Generally, this will call a Python script (e.g. `./triton/tests/test_triton.py`) that will do all the heavy lifting.

## Usage

Each pipeline creates its own `$TAG-raw` in your configured `DEST` repository. This is a compressed flashable Bootc image built for NVIDIA Jetson devices. Below is an explaination of how to run the target workflow on each

### Running Ollama

Tag: `ollama-raw`

Run `podman run --device nvidia.com/gpu=all --ipc=host ${ARTIFACT_REGISTRY_HOST}/${ARTIFACT_REGISTRY_REPO}:ollama-worker ollama serve`. This will start the Ollama server container, and standard Ollama commands can be run from there.

### Running Triton

Tag: `triton-raw`

Run `podman run --rm -d --device nvidia.com/gpu=all --ipc=host -p8000:8000 -p8001:8001 -p8002:8002 -v /models:/models nvcr.io/nvidia/tritonserver:25.07-py3-igpu tritonserver --model-repository=/models`. The Triton Inference Server is now available on localhost and can be accessed using the Triton client libraries (example given in ./triton/tests/triton-client.py).

### Running vLLM

Tag: `vllm-raw`

Run `podman run --rm -d --device nvidia.com/gpu=all --ipc=host -p8000:8000 -v /usr/share/huggingface/<your model>:/<your model> ${ARTIFACT_REGISTRY_HOST}/${ARTIFACT_REGISTRY_REPO}:vllm-worker python -m vllm.entrypoints.openai.api_server --model /<your model>` where `<your model>` is one of the configured huggingface repos from [vLLM build](#vllm-server-setup). The vLLM server is now available at port 8000 of localhost and can be interfaced with using the OpenAI client libraries.
