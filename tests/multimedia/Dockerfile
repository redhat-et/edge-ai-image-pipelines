# podman build --device nvidia.com/gpu=all --device /dev/tty0 --build-arg CACHEBUST=$(date "+%s") .
FROM nvcr.io/nvidia/l4t-jetpack:r36.4.0
ARG CACHEBUST=0
RUN sed -i "s|LDFLAGS :=|LDFLAGS := -L/usr/lib64/nvidia|" \
  /usr/src/jetson_multimedia_api/samples/Rules.mk
RUN make -C /usr/src/jetson_multimedia_api -j $(nproc)
COPY run-mmapi-tests.sh /opt/run-mmapi-tests.sh
RUN /opt/run-mmapi-tests.sh
