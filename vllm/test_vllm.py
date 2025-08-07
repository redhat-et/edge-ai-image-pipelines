import sys
import os

from jumpstarter_testing.pytest import JumpstarterTest
from jumpstarter_driver_network.adapters import FabricAdapter

USERNAME = "admin"
PASSWORD = "passwd"
WD = os.path.dirname(__file__)

for arg in sys.argv:
    if "--worker-repo=" in arg:
        worker_repo = arg.split("=")[1]

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
                ssh.sudo(
                    f"podman run --name server --network vllm --rm -d --device nvidia.com/gpu=all --ipc=host -p8000:8000 -v /usr/share/huggingface/ibm-granite/granite-vision-3.2-2b:/model ${worker_repo}:vllm-worker python -m vllm.entrypoints.openai.api_server --model /model"
                )
                ssh.sudo(
                        f"podman run --name client --network vllm --rm -it -v .:/share ${worker_repo}:vllm-worker /bin/bash /share/vllm-client.sh"
                )
            client.power.off()

