import sys
import os

from jumpstarter_testing.pytest import JumpstarterTest
from jumpstarter_driver_network.adapters import FabricAdapter

USERNAME = "admin"
PASSWORD = "passwd"
WD = os.path.dirname(__file__)

class TestVLLM(JumpstarterTest):
    def test_vllm(tmp_path, client):
        with client.log_stream():
            client.storage.dut()
            client.power.cycle()

            with client.serial.pexpect() as p:
                p.logfile = sys.stdout.buffer
                p.expect_exact("login:", timeout=600)
                p.sendline(USERNAME)
                p.expect_exact("Password:")
                p.sendline(PASSWORD)
                p.expect_exact(" ~]$")
                p.sendline("sudo systemctl start chrony-wait.service")
                p.expect_exact(" ~]$")

            with FabricAdapter(
                client=client.ssh,
                user=USERNAME,
                connect_kwargs={"password": PASSWORD},
            ) as ssh:
                ssh.put(f"{WD}/wait-for-vllm.py","wait-for-vllm.py")
                ssh.put(f"{WD}/vllm-client.py","vllm-client.py")
                ssh.put(f"{WD}/vllm-client.sh","vllm-client.sh")
                ssh.put(f"{WD}/wait-for-copy-embedded-images.sh","wait-for-copy-embedded-images.sh") 

                ssh.sudo("bash wait-for-copy-embedded-images.sh")

                result = ssh.sudo("podman network ls").stdout
                if "vllm" not in result:
                    ssh.sudo(
                        "podman network create vllm"
                    )
                ssh.sudo("podman rm -af")
                ssh.sudo("ls -R")
                ssh.sudo(
                    "podman run --name server --network vllm -d --device nvidia.com/gpu=all --ipc=host -p8000:8000 -v .:/share -v /usr/share/huggingface:/huggingface quay.io/redhat-user-workloads/octo-edge-tenant/jetson-wheels-vllm-app@sha256:4d1ed330d00308a3148cdea4495be09a05cee9cf7a114eed0ca83e40e6d58794 /bin/bash -c \"/app/bin/python -m vllm.entrypoints.openai.api_server --model /huggingface/ibm-granite/granite-vision-3.2-2b --gpu_memory_utilization=0.8 --max_model_len=8200 > /share/vllm.log\""    
                )
                ssh.sudo(
                        f"podman run --name client --network vllm --rm -it -v .:/share quay.io/redhat-user-workloads/octo-edge-tenant/jetson-wheels-vllm-app@sha256:4d1ed330d00308a3148cdea4495be09a05cee9cf7a114eed0ca83e40e6d58794 /bin/bash /share/vllm-client.sh"
                )
            client.power.off()
