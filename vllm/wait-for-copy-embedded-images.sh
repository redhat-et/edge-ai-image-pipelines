while ! systemctl status copy-embedded-images.service | grep "Active: active (exited)"; do sleep 5; done
