# Edge Pipelines for Model Validation

This repository contains several workflows to automate the building, testing, and releasing of inference stacks on the edge.

These pipelines are triggered with a simple `workflow_dispatch` event, but must be configured for your usecase first.

The result of this pipeline will be a `triton-raw` and a `triton-microshift-raw` tag in your configured `DEST_REGISTRY_REPO` containing `.raw.xz` disk images flashable to an NVIDIA Jetson device.

## Configuration

### Variables (Required)

In order to use these pipelines, a number of GitHub Repository secrets and variables must be configured.

The secrets configure authentication with three different container registries, the `SOURCE` registry contains the base RHEL Bootc image (registry.redhat.io), an `ARTIFACTS` registry where consumable artifacts are stored, and a `DEST` registry where the compiled images are stored

Required Secrets:
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

Required Variables:
* `ARTIFACT_REGISTRY_HOST`
* `ARTIFACT_REGISTRY_REPO`
* `DEST_REGISTRY_HOST`
* `DEST_REGISTRY_REPO`
* `JUMPSTARTER_SELECTOR`: Jumpstarter selector used to acquire Jumpstarter-controlled device for these workflows (passed as jmp create lease --selector $JUMPSTARTER_SELECTOR)

### Triton Inference Server setup (Required)

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

### MicroShift Setup (Optional)

By default, the MicroShift image will have two resources: the NVIDIA device plugin, and the Triton Inference Server. To add more resources to the Kustomization, find RESOURCE_DEFINITIONS in .github/workflows/build-triton.yml and append a reference (either a web URL or a path in the GitHub repository given relative to the /repo directory) to it using a space to deliminiate



