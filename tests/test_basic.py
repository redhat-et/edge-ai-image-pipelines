import sys
import os
import pytest

from pathlib import Path
from jumpstarter_testing.pytest import JumpstarterTest
from jumpstarter_driver_network.adapters import FabricAdapter

FILE = Path(os.path.realpath(__file__)).parent

USERNAME = "admin"
PASSWORD = "passwd"


class TestJetson(JumpstarterTest):
    @pytest.fixture(scope="class")
    def ssh(self, client):
        with client.log_stream():
            client.storage.flash("./image.raw")
            client.power.cycle()

            with client.serial.pexpect() as p:
                p.logfile = sys.stdout.buffer

                p.expect_exact("Enter to continue boot.", timeout=600)
                p.sendline("")

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
                yield ssh

    @pytest.mark.xfail  # not available on Jetson Thor and Jetson Orin Nano Super Developer Kit
    def test_can(self, ssh):
        assert len(ssh.sudo("ip -o link show type can").stdout.splitlines()) > 0

    def test_usb(self, ssh):
        assert len(ssh.sudo("ls -1 /sys/bus/usb/devices/").stdout.splitlines()) > 0

    def test_pcie(self, ssh):
        assert len(ssh.sudo("ls -1 /sys/bus/pci/devices/").stdout.splitlines()) > 0

    def test_hardware_video_acceleration(self, ssh):
        ssh.sudo(
            "gst-launch-1.0 videotestsrc num-buffers=300 ! nvvidconv ! nvv4l2h264enc ! nvv4l2decoder ! fakesink"
        )

    def test_cuda(self, ssh):
        tmp = ssh.run("mktemp -d").stdout.strip()
        ssh.put(FILE / "cuda" / "Dockerfile", tmp)
        ssh.sudo("podman build --no-cache --device nvidia.com/gpu=all {}".format(tmp))

    def test_dla(self, ssh):
        tmp = ssh.run("mktemp -d").stdout.strip()
        ssh.put(FILE / "dla" / "Dockerfile", tmp)
        assert "[V] [TRT] [DlaLayer]" in ssh.sudo(
            "podman build --no-cache --device nvidia.com/gpu=all {}".format(tmp)
        ).stdout

    def test_pva(self, ssh):
        tmp = ssh.run("mktemp -d").stdout.strip()
        ssh.put(FILE / "pva" / "Dockerfile", tmp)
        ssh.sudo("bash -c 'echo 0 > /sys/kernel/debug/pva0/vpu_app_authentication'")
        ssh.sudo("podman build --no-cache --device nvidia.com/gpu=all {}".format(tmp))
