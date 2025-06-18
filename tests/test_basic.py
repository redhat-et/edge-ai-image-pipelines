import sys

from jumpstarter_testing.pytest import JumpstarterTest


class TestQemu(JumpstarterTest):
    def test_driver_qemu(tmp_path, client):
        with client.log_stream():
            client.storage.flash("./image.raw")

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
