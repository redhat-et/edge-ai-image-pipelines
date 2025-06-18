import sys

from opendal import Operator

from jumpstarter_testing.pytest import JumpstarterTest


class TestQemu(JumpstarterTest):
    def test_driver_qemu(tmp_path, client):
        with client.log_stream():
            client.storage.flash(
                "pub/fedora/linux/releases/41/Cloud/x86_64/images/Fedora-Cloud-Base-Generic-41-1.4.x86_64.qcow2",
                operator=Operator(
                    "http", endpoint="https://download.fedoraproject.org"
                ),
            )

            client.power.cycle()

            with client.serial.pexpect() as p:
                p.logfile = sys.stdout.buffer
                p.expect_exact("login:", timeout=600)
                p.sendline("jumpstarter")
                p.expect_exact("Password:")
                p.sendline("password")
                p.expect_exact(" ~]$")
                p.sendline("sudo setenforce 0")
                p.expect_exact(" ~]$")

            client.power.off()
