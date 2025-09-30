FROM nvcr.io/nvidia/pytorch:25.09-py3-igpu
ARG CACHEBUST=0
RUN python3 -c 'import torch; print(torch.rand(10).cuda() * torch.rand(10).cuda())'
