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
        ssh.put("inference/tests/triton-client.yml","triton-client.yml")
        ssh.put("inference/tests/triton-client.sh","triton-client.sh")
        ssh.put("inference/tests/triton-client.py","triton-client.py")
        ssh.put("inference/tests/wait-for-microshift.sh","wait-for-microshift.sh")

        ssh.sudo("/bin/bash wait-for-microshift.sh")
        
        ssh.sudo("oc apply -f triton-client.yml")
        
        ssh.sudo("oc wait --for=condition=Available deployment/triton-inference-server --timeout 300s")
        ssh.sudo("oc wait --for=condition=Ready pod/triton-client --timeout 300s")
        
        ssh.sudo("oc exec -it triton-client -- /bin/bash /share/triton-client.sh")

    client.power.off()
