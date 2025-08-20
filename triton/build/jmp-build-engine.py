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
        ssh.put("onnx-repository.tar.xz","onnx-repository.tar.xz")
        ssh.sudo("xz -dfk onnx-repository.tar.xz")
        ssh.sudo("tar xf onnx-repository.tar")
        
        for path in ssh.sudo("find onnx-repository -name model.onnx").stdout.split('\n'):
            try:
                subpath = path.split('/',1)[1].rsplit('.',1)[0]
            except:
                print(f"WARNING: could not parse path {path}, skipping")
                continue

            ssh.sudo("podman pull nvcr.io/nvidia/tritonserver:25.07-py3-igpu")
            ssh.sudo(f"podman run --rm -it --device nvidia.com/gpu=all -v ./onnx-repository:/onnx-repository nvcr.io/nvidia/tritonserver:25.07-py3-igpu /usr/src/tensorrt/bin/trtexec --onnx=/onnx-repository/{subpath}.onnx --saveEngine=/onnx-repository/{subpath}.plan ")
            ssh.sudo(f"rm -f {path}")

        ssh.sudo("mv onnx-repository plan-repository")
        ssh.sudo("tar cf plan-repository.tar plan-repository")
        ssh.sudo("xz plan-repository.tar")
        ssh.get("plan-repository.tar.xz","plan-repository.tar.xz")
    client.power.off()
