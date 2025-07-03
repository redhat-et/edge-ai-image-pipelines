import sys

from jumpstarter_driver_network.adapters import FabricAdapter

from jumpstarter.utils.env import env

HOSTNAME = "localhost"
USERNAME = "admin"
PASSWORD = "passwd"

# init jumpstarter client from env (jmp shell)
with env() as client:
    # ensure the usb dirve is connected to the dut
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
        ssh.put("inference/tis-client.py","tis-client.py")
        ssh.put("inference/tis-client.sh","tis-client.sh")
        
        result = ssh.sudo("podman network ls").stdout
        if "triton" not in result:
            ssh.sudo(
                "podman network create triton"
            )
        ssh.sudo("podman rm -af")
        ssh.sudo("ls -R") 
        ssh.sudo(
                "podman run --name server --network trition -p8000:8000 --rm -d --device nvidia.com/gpu=all --ipc=host -v .:/share nvcr.io/nvidia/tritonserver:25.05-py3-igpu tritonserver --model-repository=/share/models"
        )
        ssh.sudo(
                "podman run --name client --network triton --rm -it -v .:/share nvcr.io/nvidia/tritonserver:25.05-py3-igpu /bin/bash /share/tis-client.sh"
        )

    client.power.off()
