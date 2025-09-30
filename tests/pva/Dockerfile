# sudo bash -c 'echo 0 > /sys/kernel/debug/pva0/vpu_app_authentication'
# podman build --device nvidia.com/gpu=all .
FROM ubuntu:24.04

RUN apt-get update
RUN apt-get install -y gnupg ca-certificates cmake make g++ libegl1
RUN apt-key adv --fetch-key https://repo.download.nvidia.com/jetson/jetson-ota-public.asc
RUN cat <<EOF > /etc/apt/sources.list.d/jetson.list
deb https://repo.download.nvidia.com/jetson/common r36.4 main
EOF

RUN apt-get update
RUN apt-get install -y libnvvpi3 vpi3-dev vpi3-samples
RUN vpi3_install_samples.sh /samples
RUN cmake -S /samples/NVIDIA_VPI-3.2-samples/05-benchmark/ -B /build
RUN cmake --build /build/
ARG CACHEBUST=0
RUN /build/vpi_sample_05_benchmark cuda
RUN /build/vpi_sample_05_benchmark pva
RUN /build/vpi_sample_05_benchmark cpu
