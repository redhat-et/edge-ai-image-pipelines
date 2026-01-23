# echo 0 > /sys/kernel/debug/pva0/vpu_app_authentication
# podman build --device nvidia.com/gpu=all --build-arg CACHEBUST=$(date "+%s") .
FROM nvcr.io/nvidia/l4t-jetpack:r36.4.0
RUN apt-get update && apt-get install -y cmake
ARG CACHEBUST=0
RUN for dir in /opt/nvidia/vpi3/samples/*; do \
  cmake -S ${dir} -B ${dir}/build && cmake --build ${dir}/build; \
done
COPY run-vpi-tests.sh /opt/run-vpi-tests.sh
RUN /opt/run-vpi-tests.sh
