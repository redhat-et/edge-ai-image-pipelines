import sys

from jumpstarter_testing.pytest import JumpstarterTest
from jumpstarter_driver_network.adapters import FabricAdapter

USERNAME = "admin"
PASSWORD = "passwd"


class TestTriton(JumpstarterTest):
    def test_driver_qemu(tmp_path, client):
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
                ssh.put("triton/tests/triton-client.py","triton-client.py")
                ssh.put("triton/tests/triton-client.sh","triton-client.sh")
                
                result = ssh.sudo("podman network ls").stdout
                if "triton" not in result:
                    ssh.sudo(
                        "podman network create triton"
                    )
                ssh.sudo("podman rm -af")
                ssh.sudo("ls -R") 
                ssh.sudo(
                        "podman run --name server --network triton -p8000:8000 --rm -d --device nvidia.com/gpu=all --ipc=host -v /:/share nvcr.io/nvidia/tritonserver:25.05-py3-igpu tritonserver --model-repository=/share/models"
                )
                ssh.sudo(
                        "podman run --name client --network triton --rm -it -v .:/share nvcr.io/nvidia/tritonserver:25.05-py3-igpu /bin/bash /share/triton-client.sh"
                )
            client.power.off()

