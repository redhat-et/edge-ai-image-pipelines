python3 inference/jmp-build-engine.py
podman artifact add quay.io/redhat-et/rhel-bootc-tegra:model-plan model.plan
podman artifact push quay.io/redhat-et/rhel-bootc-tegra:model-plan
