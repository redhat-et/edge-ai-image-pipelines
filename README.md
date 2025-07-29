# Edge Pipelines for Model Validation

This repository contains several workflows to automate the building, testing, and releasing of inference stacks on the edge.

These pipelines are triggered with a simple `workflow_dispatch` or `push` event, but must be configured for your usecase first.

The result of this pipeline will be a number of tags in your configured `DEST_REGISTRY_REPO` containing both Bootc container images and `.raw.xz` compressed Bootc disk images flashable to an NVIDIA Jetson device.

The tags are:
* `base`: a base image containing the necessary JetPack drivers to run AI workflows
* `ollama`: ollama LLM runtime
* `vllm`: vllm LLM runtime
* `triton`: Triton Inference Server
* `ollama-with-models`: Example of how to physically embed models with the ollama image
* `vllm-with-models`: Example of how to physically embed models with the vllm image

For each tag TAG, `${TAG}-raw` will also be generated with the flashable Bootc image

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

### Triton Inference Server setup

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

The pipeline will then automatically compile these models into .plan format using the pipeline's jumpstarter device and reupload it to `ARTIFACT_REGISTRY_REPO` under the tag plan-repository

### MicroShift Workflow

If you'd like to deploy application containers (e.g. Triton Inference Server, vLLM) on MicroShift, use the "Add MicroShift to Bootc Image" workflow. It will install MicroShift along with the resources required to give your MicroShift pods access to the iGPU.

The `workflow_dispatch` event has the following inputs:
* `resource_definitions`: a space-delimited list of resources to apply as Kustomizations. These can either be Web URLs or paths within this repository given relative to the `/repo` mount. (e.g. `./inference/microshift/triton.yml` would be given as `/repo/inference/build/triton.yml`)
* `input_image`: A reference to the Bootc container image that MicroShift should be added to
* `tags_list`: Tag list to apply to the output image

The flashable bootc image will be pushed to `$DEST_REGISTRY_HOST/$DEST_REGISTRY_REPO:$tag` for each tag in `tags_list`
