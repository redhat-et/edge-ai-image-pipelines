# Automated AI Inferencing Pipelines for Edge Deployment using Jumpstarter

This proposal outlines the implementation of automated AI inferencing pipelines for edge deployment on NVIDIA Jetson AGX (and NX) devices utilizing a Red Hat Enterprise Linux (RHEL) image. The pipelines will integrate multiple AI inferencing stacks, including **vLLM**, **llama.cpp**, and a designated **Model Under Test (MUT)**, facilitated by **Jumpstarter** as the enabling tool. Automation will be achieved through a CI/CD tool (e.g., GitHub Actions, GitLab Runner, Tekton Pipelines).

## Pipeline Steps

1. **Code Development & Commit**  
   Commit AI model configs, scripts, and pipelines to a version control system.

2. **CI/CD Trigger**  
   Trigger the pipeline on code commits or on a schedule.

3. **Image Creation**  
   - Build a custom image based on a RHEL + NVIDIA driver **bootc** image.
   - Integrate either `vLLM` or `llama.cpp` with the MUT.
   - Create a separate image for each inference stack.

4. **Deployment via Jumpstarter**  
   Install the created image onto the AGX or NX device using Jumpstarter.

5. **Testing & Validation**  
   Run inference performance tests and validate results. Gather logs.

6. **Artifact Storage**  
   Store optimized images in a repository.

## Implementation Details

- **CI/CD Tool**  
  Select a suitable CI/CD tool (e.g., GitHub Actions) and configure pipelines with YAML.

- **Image Building**  
  Build custom images with either `vLLM`, `llama.cpp`, or other inference servers + MUT on top of the RHEL + NVIDIA driver **bootc** base image.

- **Jumpstarter Deployment**  
  Use Jumpstarter to install custom images on target devices.

- **Testing**  
  Run performance tests and gather logs for each image.

- **Artifact Repository**  
  Store created images for deployment.

## Benefits

- **Automation**: Streamlined testing and deployment of inferencing stacks.  
- **Comparison**: Easy comparison between `vLLM` and `llama.cpp` performance via separate pipelines.  
- **Efficiency**: Faster development cycles.  
- **Consistency**: Repeatable processes with **bootc** base images.

