import sys

from jumpstarter_testing.pytest import JumpstarterTest
from jumpstarter_driver_network.adapters import FabricAdapter

USERNAME = "admin"
PASSWORD = "passwd"

class TestTritonMicroshift(JumpstarterTest):
    def test_triton_microshift(tmp_path, client):
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
                ssh.sudo("chown -R admin:admin /var/home/admin")
                ssh.put("triton/tests/triton-client.yml","triton-client.yml")
                ssh.put("triton/tests/triton-client.sh","triton-client.sh")
                ssh.put("triton/tests/triton-client.py","triton-client.py")
                ssh.put("triton/tests/wait-for-microshift.sh","wait-for-microshift.sh")

                ssh.sudo("/bin/bash wait-for-microshift.sh")
                
                ssh.sudo("oc apply -f triton-client.yml")
                
                ssh.sudo("oc wait --for=condition=Available deployment/triton-inference-server --timeout 300s")
                ssh.sudo("oc wait --for=condition=Ready pod/triton-client --timeout 300s")
                
                ssh.sudo("oc exec -it triton-client -- /bin/bash /share/triton-client.sh")
            client.power.off()

