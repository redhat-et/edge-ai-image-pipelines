import sys
import os

from jumpstarter_testing.pytest import JumpstarterTest
from jumpstarter_driver_network.adapters import FabricAdapter

USERNAME = "admin"
PASSWORD = "passwd"
WD = os.path.dirname(__file__)

worker_repo = os.getenv("WORKER_REPO")

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
                ssh.put(f"{WD}/vllm-client.py","vllm-client.py")
                ssh.put(f"{WD}/vllm-client.sh","vllm-client.sh")
                
                result = ssh.sudo("podman network ls").stdout
                if "vllm" not in result:
                    ssh.sudo(
                        "podman network create vllm"
                    )
                ssh.sudo("podman rm -af")
                ssh.sudo("ls -R")
                print(f"{worker_repo}:vllm-worker")
                ssh.sudo(
                    f"podman run --name server --network vllm --rm -d --device nvidia.com/gpu=all --ipc=host -p8000:8000 -v ./granite:/granite {worker_repo}:vllm-worker python -m vllm.entrypoints.openai.api_server --model /granite"
                )
                ssh.sudo(
                        f"podman run --name client --network vllm --rm -it -v .:/share {worker_repo}:vllm-worker /bin/bash /share/vllm-client.sh"
                )
            client.power.off()

