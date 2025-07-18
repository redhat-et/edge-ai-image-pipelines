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
        print("fetching repoistory")
        ssh.put("onnx-repository.tar.xz","onnx-repository.tar.xz")
        print("processing")
        ssh.sudo("xz -d onnx-repository.tar.xz")
        ssh.sudo("tar xf onnx-repository.tar")
        ssh.sudo("find onnx-repository -type d -exec mkdir -p plan-repository{} \\;")
        ssh.sudo(
            """
            find onnx-repository -name *.onnx -exec \
                podman run --rm -it --device nvidia.com/gpu=all \
                    -v onnx-repository:/onnx-repository \
                    -v plan-repository:/plan-repository \
                    nvcr.io/nvidia/tensorrt:25.05-py3-igpu \
                        trtexec --onnx=/{} --saveEngine=/{} \
            \\;
            """
        )
        ssh.sudo("tar cf plan-repository.tar plan-repository")
        ssh.sudo("xz plan-repository.tar")
        print("storing repository...")
        ssh.get("plan-repository.tar.xz","plan-repository.tar.xz")
    client.power.off()
