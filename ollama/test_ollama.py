import sys

from jumpstarter_testing.pytest import JumpstarterTest
from jumpstarter_driver_network.adapters import FabricAdapter

USERNAME = "admin"
PASSWORD = "passwd"


class TestOllama(JumpstarterTest):
    def test_ollama(tmp_path, client):
        with client.log_stream():
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
                ssh.sudo(
                    "podman run --name ollama -d -i --rm --device nvidia.com/gpu=all "
                    f"{sys.argv[1]}"
                )
                assert (
                    "library=cuda variant=jetpack6 compute=8.7 driver=12.6 name=Orin"
                    in ssh.sudo("podman exec ollama cat /data/logs/ollama.log").stdout
                )
                ssh.sudo("podman stop ollama")

            client.power.off()
