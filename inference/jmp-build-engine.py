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
        ssh.put("model.onnx","model.onnx")
        ssh.sudo("mkdir -p share")
        ssh.sudo("mv model.onnx share")
        ssh.sudo(
            "podman run --name trtexec -i --rm --device nvidia.com/gpu=all -v ./share:/share --replace nvcr.io/nvidia/tensorrt:25.05-py3-igpu trtexec --onnx=/share/model.onnx --saveEngine=/share/model.plan"
        )
        ssh.get("share/model.plan","model.plan")

    client.power.off()
